"""
User Feedback System for RAG Fine-tuning

This module implements a feedback loop that:
1. Collects user ratings (thumbs up/down) on answers
2. Logs feedback with contextual information
3. Automatically adjusts retrieval parameters based on feedback patterns
4. Fine-tunes reranker thresholds and K values
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import statistics

logger = logging.getLogger(__name__)

@dataclass
class FeedbackEntry:
    """Individual feedback entry"""
    feedback_id: str
    session_id: str
    query: str
    answer: str
    rating: str  # 'positive' or 'negative'
    timestamp: str
    retrieval_method: str
    retrieval_k: int
    rerank_threshold: float
    quality_score: Optional[float] = None
    confidence_score: Optional[float] = None
    context_chunks: Optional[List[str]] = None
    response_time: Optional[float] = None
    user_comment: Optional[str] = None

@dataclass
class ParameterAdjustment:
    """Parameter adjustment recommendation"""
    parameter_name: str
    old_value: float
    new_value: float
    reason: str
    confidence: float
    timestamp: str

class FeedbackSystem:
    """
    Feedback collection and parameter optimization system
    """
    
    def __init__(self, 
                 feedback_file: str = "data/user_feedback.json",
                 adjustments_file: str = "data/parameter_adjustments.json",
                 config_file: str = "data/feedback_config.json"):
        """
        Initialize feedback system
        
        Args:
            feedback_file: File to store user feedback entries
            adjustments_file: File to store parameter adjustments
            config_file: File to store feedback configuration
        """
        self.feedback_file = Path(feedback_file)
        self.adjustments_file = Path(adjustments_file)
        self.config_file = Path(config_file)
        
        # Create data directory
        self.feedback_file.parent.mkdir(exist_ok=True)
        
        # In-memory storage for fast access
        self.feedback_entries = deque(maxlen=1000)  # Keep last 1000 feedback entries
        self.recent_adjustments = deque(maxlen=100)  # Keep last 100 adjustments
        
        # Feedback analysis configuration
        self.config = {
            'min_feedback_for_adjustment': 5,  # Minimum feedback entries before adjusting
            'adjustment_sensitivity': 0.7,    # Sensitivity for parameter changes (0-1)
            'negative_feedback_threshold': 0.4, # Threshold for considering adjustment
            'positive_feedback_boost': 0.8,   # Threshold for positive reinforcement
            'k_adjustment_range': (3, 15),    # Min/max K values
            'rerank_threshold_range': (0.1, 0.9), # Min/max rerank thresholds
            'adjustment_cooldown_hours': 2,   # Hours between adjustments
            'quality_weight': 0.6,           # Weight for quality scores in decisions
            'user_rating_weight': 0.4,       # Weight for user ratings in decisions
        }
        
        # Current optimal parameters (will be updated based on feedback)
        self.optimal_params = {
            'retrieval_k': 5,
            'rerank_threshold': 0.7,
            'hybrid_weight': 0.5,
            'quality_threshold': 3.0,
        }
        
        # Load existing data
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing feedback and configuration data"""
        try:
            # Load feedback entries
            if self.feedback_file.exists():
                with open(self.feedback_file, 'r') as f:
                    stored_feedback = json.load(f)
                    for entry_data in stored_feedback[-1000:]:  # Load last 1000
                        entry = FeedbackEntry(**entry_data)
                        self.feedback_entries.append(entry)
            
            # Load adjustments
            if self.adjustments_file.exists():
                with open(self.adjustments_file, 'r') as f:
                    stored_adjustments = json.load(f)
                    for adj_data in stored_adjustments[-100:]:  # Load last 100
                        adjustment = ParameterAdjustment(**adj_data)
                        self.recent_adjustments.append(adjustment)
            
            # Load configuration
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config.get('config', {}))
                    self.optimal_params.update(saved_config.get('optimal_params', {}))
                    
            logger.info(f"Loaded {len(self.feedback_entries)} feedback entries and {len(self.recent_adjustments)} adjustments")
            
        except Exception as e:
            logger.warning(f"Could not load existing feedback data: {e}")
    
    def _save_data(self):
        """Save feedback data and configuration to files"""
        try:
            # Save feedback entries
            with open(self.feedback_file, 'w') as f:
                feedback_data = [asdict(entry) for entry in self.feedback_entries]
                json.dump(feedback_data, f, indent=2)
            
            # Save adjustments
            with open(self.adjustments_file, 'w') as f:
                adjustments_data = [asdict(adj) for adj in self.recent_adjustments]
                json.dump(adjustments_data, f, indent=2)
            
            # Save configuration and optimal parameters
            with open(self.config_file, 'w') as f:
                config_data = {
                    'config': self.config,
                    'optimal_params': self.optimal_params,
                    'last_updated': datetime.now().isoformat()
                }
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Could not save feedback data: {e}")
    
    def log_feedback(self, 
                    session_id: str,
                    query: str,
                    answer: str,
                    rating: str,
                    retrieval_method: str,
                    retrieval_k: int,
                    rerank_threshold: float,
                    quality_score: Optional[float] = None,
                    confidence_score: Optional[float] = None,
                    context_chunks: Optional[List[str]] = None,
                    response_time: Optional[float] = None,
                    user_comment: Optional[str] = None) -> str:
        """
        Log user feedback for an answer
        
        Args:
            session_id: User session identifier
            query: Original query
            answer: Generated answer
            rating: 'positive' or 'negative'
            retrieval_method: Method used for retrieval
            retrieval_k: K value used
            rerank_threshold: Reranker threshold used
            quality_score: Optional quality score
            confidence_score: Optional confidence score
            context_chunks: Optional context chunks used
            response_time: Optional response time
            user_comment: Optional user comment
            
        Returns:
            feedback_id: Unique identifier for this feedback entry
        """
        
        feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_id[:8]}"
        
        feedback_entry = FeedbackEntry(
            feedback_id=feedback_id,
            session_id=session_id,
            query=query,
            answer=answer,
            rating=rating,
            timestamp=datetime.now().isoformat(),
            retrieval_method=retrieval_method,
            retrieval_k=retrieval_k,
            rerank_threshold=rerank_threshold,
            quality_score=quality_score,
            confidence_score=confidence_score,
            context_chunks=context_chunks,
            response_time=response_time,
            user_comment=user_comment
        )
        
        self.feedback_entries.append(feedback_entry)
        
        # Save data
        try:
            self._save_data()
        except Exception as e:
            logger.error(f"Error saving feedback data: {e}")
        
        # Check if we should adjust parameters
        try:
            self._check_for_parameter_adjustments()
        except Exception as e:
            logger.error(f"Error checking parameter adjustments: {e}")
        
        logger.info(f"Logged {rating} feedback for query: {query[:50]}...")
        return feedback_id
    
    def _check_for_parameter_adjustments(self):
        """
        Check if parameters should be adjusted based on recent feedback
        """
        try:
            # Get recent feedback (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_feedback = [
                entry for entry in self.feedback_entries
                if datetime.fromisoformat(entry.timestamp) > cutoff_time
            ]
            
            if len(recent_feedback) < self.config['min_feedback_for_adjustment']:
                logger.debug(f"Not enough recent feedback ({len(recent_feedback)}) for parameter adjustment")
                return
            
            # Check cooldown period
            if self._is_in_cooldown_period():
                logger.debug("In cooldown period, skipping parameter adjustments")
                return
            
            # Analyze feedback patterns and suggest adjustments
            adjustments = self._analyze_feedback_patterns(recent_feedback)
            
            if adjustments:
                logger.info(f"Applying {len(adjustments)} parameter adjustments")
                # Apply adjustments
                for adjustment in adjustments:
                    self._apply_parameter_adjustment(adjustment)
            else:
                logger.debug("No parameter adjustments needed")
                
        except Exception as e:
            logger.error(f"Error in parameter adjustment check: {e}")
            # Don't let this fail the feedback submission
    
    def _is_in_cooldown_period(self) -> bool:
        """Check if we're in cooldown period since last adjustment"""
        if not self.recent_adjustments:
            return False
        
        last_adjustment = self.recent_adjustments[-1]
        last_adjustment_time = datetime.fromisoformat(last_adjustment.timestamp)
        cooldown_end = last_adjustment_time + timedelta(hours=self.config['adjustment_cooldown_hours'])
        
        return datetime.now() < cooldown_end
    
    def _analyze_feedback_patterns(self, feedback_entries: List[FeedbackEntry]) -> List[ParameterAdjustment]:
        """
        Analyze feedback patterns and suggest parameter adjustments
        
        Args:
            feedback_entries: List of recent feedback entries
            
        Returns:
            List of parameter adjustments to apply
        """
        adjustments = []
        
        # Group feedback by parameters
        param_groups = defaultdict(list)
        
        for entry in feedback_entries:
            key = f"k{entry.retrieval_k}_thresh{entry.rerank_threshold:.2f}_method{entry.retrieval_method}"
            param_groups[key].append(entry)
        
        # Analyze each parameter combination
        for param_key, entries in param_groups.items():
            if len(entries) < 3:  # Need at least 3 feedback entries
                continue
            
            try:
                # Calculate performance metrics
                positive_ratio = len([e for e in entries if e.rating == 'positive']) / len(entries)
                
                # Safely calculate averages with empty list handling
                quality_scores = [e.quality_score for e in entries if e.quality_score is not None]
                confidence_scores = [e.confidence_score for e in entries if e.confidence_score is not None]
                response_times = [e.response_time for e in entries if e.response_time is not None]
                
                avg_quality = statistics.mean(quality_scores) if quality_scores else 0.0
                avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.0
                avg_response_time = statistics.mean(response_times) if response_times else 0.0
                
                # Calculate combined score
                combined_score = (
                    positive_ratio * self.config.get('user_rating_weight', 0.4) +
                    (avg_quality / 5.0) * self.config.get('quality_weight', 0.6)
                )
                
                # Check if adjustments are needed
                if combined_score < self.config['negative_feedback_threshold']:
                    # Poor performance - suggest improvements
                    adjustments.extend(self._suggest_improvements(entries[0], combined_score))
                elif combined_score > self.config['positive_feedback_boost']:
                    # Great performance - reinforce parameters
                    adjustments.extend(self._reinforce_parameters(entries[0], combined_score))
                    
            except Exception as e:
                logger.error(f"Error analyzing feedback pattern for {param_key}: {e}")
                continue  # Skip this parameter group and continue with others
        
        return adjustments
    
    def _suggest_improvements(self, sample_entry: FeedbackEntry, performance_score: float) -> List[ParameterAdjustment]:
        """
        Suggest parameter improvements for poor performing configurations
        
        Args:
            sample_entry: Sample entry from the poor performing group
            performance_score: Combined performance score
            
        Returns:
            List of suggested adjustments
        """
        adjustments = []
        current_time = datetime.now().isoformat()
        
        # Adjust K value
        current_k = sample_entry.retrieval_k
        if current_k < 8:  # Increase K for better recall
            new_k = min(current_k + 2, self.config['k_adjustment_range'][1])
            adjustments.append(ParameterAdjustment(
                parameter_name='retrieval_k',
                old_value=current_k,
                new_value=new_k,
                reason=f'Increasing K from {current_k} to {new_k} due to poor performance (score: {performance_score:.3f})',
                confidence=0.8,
                timestamp=current_time
            ))
        elif current_k > 5:  # Decrease K for better precision
            new_k = max(current_k - 1, self.config['k_adjustment_range'][0])
            adjustments.append(ParameterAdjustment(
                parameter_name='retrieval_k',
                old_value=current_k,
                new_value=new_k,
                reason=f'Decreasing K from {current_k} to {new_k} due to poor performance (score: {performance_score:.3f})',
                confidence=0.7,
                timestamp=current_time
            ))
        
        # Adjust reranker threshold
        current_threshold = sample_entry.rerank_threshold
        if current_threshold > 0.5:  # Lower threshold for more permissive reranking
            new_threshold = max(current_threshold - 0.1, self.config['rerank_threshold_range'][0])
            adjustments.append(ParameterAdjustment(
                parameter_name='rerank_threshold',
                old_value=current_threshold,
                new_value=new_threshold,
                reason=f'Lowering rerank threshold from {current_threshold:.2f} to {new_threshold:.2f} due to poor performance',
                confidence=0.7,
                timestamp=current_time
            ))
        
        return adjustments
    
    def _reinforce_parameters(self, sample_entry: FeedbackEntry, performance_score: float) -> List[ParameterAdjustment]:
        """
        Reinforce parameters that are performing well
        
        Args:
            sample_entry: Sample entry from the well performing group
            performance_score: Combined performance score
            
        Returns:
            List of reinforcement adjustments
        """
        adjustments = []
        current_time = datetime.now().isoformat()
        
        # Update optimal parameters
        self.optimal_params['retrieval_k'] = sample_entry.retrieval_k
        self.optimal_params['rerank_threshold'] = sample_entry.rerank_threshold
        
        adjustments.append(ParameterAdjustment(
            parameter_name='optimal_params_update',
            old_value=0,
            new_value=1,
            reason=f'Updating optimal parameters based on excellent performance (score: {performance_score:.3f})',
            confidence=0.9,
            timestamp=current_time
        ))
        
        return adjustments
    
    def _apply_parameter_adjustment(self, adjustment: ParameterAdjustment):
        """
        Apply a parameter adjustment
        
        Args:
            adjustment: Parameter adjustment to apply
        """
        self.recent_adjustments.append(adjustment)
        
        if adjustment.parameter_name == 'retrieval_k':
            self.optimal_params['retrieval_k'] = int(adjustment.new_value)
        elif adjustment.parameter_name == 'rerank_threshold':
            self.optimal_params['rerank_threshold'] = adjustment.new_value
        
        logger.info(f"Applied adjustment: {adjustment.reason}")
        
        # Save the updated configuration
        self._save_data()
    
    def get_optimal_parameters(self) -> Dict[str, float]:
        """
        Get current optimal parameters based on feedback analysis
        
        Returns:
            Dictionary of optimal parameters
        """
        return self.optimal_params.copy()
    
    def get_feedback_summary(self, hours: int = 24) -> Dict:
        """
        Get feedback summary for the specified time period
        
        Args:
            hours: Time period in hours
            
        Returns:
            Dictionary with feedback summary statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_feedback = [
            entry for entry in self.feedback_entries
            if datetime.fromisoformat(entry.timestamp) > cutoff_time
        ]
        
        if not recent_feedback:
            return {
                'total_feedback': 0,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'avg_quality_score': 0,
                'avg_confidence_score': 0,
                'recent_adjustments': []
            }
        
        positive_count = len([e for e in recent_feedback if e.rating == 'positive'])
        negative_count = len([e for e in recent_feedback if e.rating == 'negative'])
        
        quality_scores = [e.quality_score for e in recent_feedback if e.quality_score is not None]
        confidence_scores = [e.confidence_score for e in recent_feedback if e.confidence_score is not None]
        
        # Get recent adjustments
        recent_adjustments = [
            asdict(adj) for adj in self.recent_adjustments
            if datetime.fromisoformat(adj.timestamp) > cutoff_time
        ]
        
        return {
            'total_feedback': len(recent_feedback),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'positive_ratio': positive_count / len(recent_feedback),
            'negative_ratio': negative_count / len(recent_feedback),
            'avg_quality_score': statistics.mean(quality_scores) if quality_scores else 0,
            'avg_confidence_score': statistics.mean(confidence_scores) if confidence_scores else 0,
            'recent_adjustments': recent_adjustments,
            'optimal_parameters': self.optimal_params
        }
    
    def get_feedback_entries(self, limit: int = 50) -> List[Dict]:
        """
        Get recent feedback entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of feedback entries as dictionaries
        """
        recent_entries = list(self.feedback_entries)[-limit:]
        return [asdict(entry) for entry in reversed(recent_entries)]

# Global feedback system instance
_feedback_system = None

def get_feedback_system() -> FeedbackSystem:
    """Get global feedback system instance"""
    global _feedback_system
    if _feedback_system is None:
        _feedback_system = FeedbackSystem()
    return _feedback_system 