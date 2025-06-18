"""
Advanced Answer Evaluation & Quality Control System

This module implements LLM-as-a-Judge for automatic answer quality grading,
answer confidence scoring, and quality monitoring over time.
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)

@dataclass
class AnswerQualityMetrics:
    """Structured representation of answer quality metrics"""
    faithfulness_score: float  # 0-5: How well answer is grounded in context
    relevance_score: float     # 0-5: How relevant answer is to query
    completeness_score: float  # 0-5: How complete the answer is
    clarity_score: float       # 0-5: How clear and understandable the answer is
    overall_score: float       # 0-5: Overall quality rating
    confidence_score: float    # 0-1: Confidence in the answer
    timestamp: str
    query: str
    answer: str
    context_quality: float     # 0-1: Quality of retrieved context
    processing_time: float     # Time taken to generate answer
    
@dataclass
class QualityTrend:
    """Tracking quality trends over time"""
    period: str  # "hour", "day", "week"
    avg_overall_score: float
    avg_confidence: float
    total_queries: int
    low_quality_count: int  # Scores below 2.5
    timestamp: str

class AnswerEvaluator:
    """LLM-as-a-Judge system for answer quality evaluation"""
    
    def __init__(self, 
                 ollama_runner=None,
                 metrics_file: str = "data/answer_metrics.json",
                 trends_file: str = "data/quality_trends.json"):
        self.ollama_runner = ollama_runner
        self.metrics_file = Path(metrics_file)
        self.trends_file = Path(trends_file)
        
        # Create data directory if it doesn't exist
        self.metrics_file.parent.mkdir(exist_ok=True)
        
        # Load existing metrics
        self.metrics_history = self._load_metrics()
        self.quality_trends = self._load_trends()
        
    def _load_metrics(self) -> List[Dict]:
        """Load metrics history from file"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load metrics file: {e}")
        return []
    
    def _load_trends(self) -> List[Dict]:
        """Load quality trends from file"""
        try:
            if self.trends_file.exists():
                with open(self.trends_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load trends file: {e}")
        return []
    
    def _save_metrics(self):
        """Save metrics history to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save metrics: {e}")
    
    def _save_trends(self):
        """Save quality trends to file"""
        try:
            with open(self.trends_file, 'w') as f:
                json.dump(self.quality_trends, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save trends: {e}")
    
    def evaluate_answer_quality(self, 
                               query: str,
                               answer: str,
                               context: List[str],
                               processing_time: float = 0.0) -> AnswerQualityMetrics:
        """
        Evaluate answer quality using LLM-as-a-Judge approach
        
        Args:
            query: User query
            answer: Generated answer
            context: Retrieved context chunks
            processing_time: Time taken to generate answer
            
        Returns:
            AnswerQualityMetrics with detailed scoring
        """
        start_time = time.time()
        
        # Calculate context quality
        context_quality = self._assess_context_quality(query, context)
        
        # Generate evaluation using LLM
        evaluation_scores = self._llm_judge_evaluation(query, answer, context)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            evaluation_scores, context_quality, len(context)
        )
        
        # Create metrics object
        metrics = AnswerQualityMetrics(
            faithfulness_score=evaluation_scores.get("faithfulness", 3.0),
            relevance_score=evaluation_scores.get("relevance", 3.0),
            completeness_score=evaluation_scores.get("completeness", 3.0),
            clarity_score=evaluation_scores.get("clarity", 3.0),
            overall_score=evaluation_scores.get("overall", 3.0),
            confidence_score=confidence_score,
            timestamp=datetime.now().isoformat(),
            query=query,
            answer=answer,
            context_quality=context_quality,
            processing_time=processing_time
        )
        
        # Store metrics
        self.metrics_history.append(asdict(metrics))
        self._save_metrics()
        
        # Update trends
        self._update_quality_trends(metrics)
        
        logger.info(f"Answer evaluation completed in {time.time() - start_time:.2f}s - Overall Score: {metrics.overall_score:.2f}")
        
        return metrics
    
    def _llm_judge_evaluation(self, query: str, answer: str, context: List[str]) -> Dict[str, float]:
        """Use LLM to evaluate answer quality across multiple dimensions"""
        
        context_text = "\n\n".join(context) if context else "No context available"
        
        evaluation_prompt = f"""You are an expert evaluator tasked with rating the quality of an AI assistant's answer. Please evaluate the answer across four dimensions and provide scores from 0-5 (where 5 is excellent and 0 is very poor).

QUERY: {query}

CONTEXT PROVIDED:
{context_text}

ANSWER TO EVALUATE:
{answer}

Please rate the answer on these dimensions:

1. FAITHFULNESS (0-5): How well is the answer grounded in the provided context?
2. RELEVANCE (0-5): How relevant is the answer to the specific query?  
3. COMPLETENESS (0-5): How complete is the answer given the available context?
4. CLARITY (0-5): How clear and understandable is the answer?

Please respond in this exact format:
FAITHFULNESS: [score]
RELEVANCE: [score]  
COMPLETENESS: [score]
CLARITY: [score]
OVERALL: [average of the four scores]"""

        try:
            if self.ollama_runner and hasattr(self.ollama_runner, 'llm') and self.ollama_runner.llm:
                # Direct LLM call to avoid recursion
                evaluation_response = self.ollama_runner.llm.invoke(evaluation_prompt)
                
                # Parse scores from response
                scores = self._parse_evaluation_scores(evaluation_response)
                if scores:
                    return scores
                
        except Exception as e:
            logger.warning(f"LLM evaluation failed: {e}")
        
        # Fallback: heuristic-based evaluation
        return self._heuristic_evaluation(query, answer, context)
    
    def _parse_evaluation_scores(self, evaluation_response: str) -> Optional[Dict[str, float]]:
        """Parse LLM evaluation response to extract scores"""
        try:
            lines = evaluation_response.strip().split('\n')
            scores = {}
            
            for line in lines:
                line = line.strip().upper()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Extract numeric score
                    try:
                        score = float(value.split()[0])  # Get first number
                        if 0 <= score <= 5:
                            if key.startswith('FAITH'):
                                scores['faithfulness'] = score
                            elif key.startswith('RELEV'):
                                scores['relevance'] = score
                            elif key.startswith('COMPL'):
                                scores['completeness'] = score
                            elif key.startswith('CLAR'):
                                scores['clarity'] = score
                            elif key.startswith('OVER'):
                                scores['overall'] = score
                    except (ValueError, IndexError):
                        continue
            
            # Validate we have all required scores
            required_keys = ['faithfulness', 'relevance', 'completeness', 'clarity']
            if all(key in scores for key in required_keys):
                if 'overall' not in scores:
                    scores['overall'] = sum(scores[key] for key in required_keys) / len(required_keys)
                return scores
                
        except Exception as e:
            logger.warning(f"Could not parse evaluation scores: {e}")
        
        return None
    
    def _heuristic_evaluation(self, query: str, answer: str, context: List[str]) -> Dict[str, float]:
        """Fallback heuristic-based evaluation when LLM evaluation fails"""
        
        context_text = " ".join(context).lower() if context else ""
        query_lower = query.lower()
        answer_lower = answer.lower()
        
        # Faithfulness: check if answer content appears in context
        faithfulness = 3.0  # Default
        if context_text:
            answer_words = set(answer_lower.split())
            context_words = set(context_text.split())
            overlap = len(answer_words.intersection(context_words))
            faithfulness = min(5.0, max(1.0, (overlap / max(len(answer_words), 1)) * 5))
        
        # Relevance: check query-answer keyword overlap
        query_words = set(query_lower.split())
        answer_words = set(answer_lower.split())
        relevance_overlap = len(query_words.intersection(answer_words))
        relevance = min(5.0, max(1.0, (relevance_overlap / max(len(query_words), 1)) * 5))
        
        # Completeness: based on answer length and context usage
        completeness = 3.0
        if len(answer.split()) >= 20:  # Reasonable length
            completeness += 1.0
        if context and len(context) > 1:  # Multiple context sources used
            completeness += 0.5
        completeness = min(5.0, completeness)
        
        # Clarity: based on answer structure and length
        clarity = 3.0
        if len(answer.split()) >= 10:  # Not too short
            clarity += 0.5
        if len(answer.split()) <= 200:  # Not too long
            clarity += 0.5
        if answer.count('.') >= 2:  # Multiple sentences
            clarity += 0.5
        clarity = min(5.0, clarity)
        
        overall = (faithfulness + relevance + completeness + clarity) / 4
        
        return {
            'faithfulness': faithfulness,
            'relevance': relevance,
            'completeness': completeness,
            'clarity': clarity,
            'overall': overall
        }
    
    def _assess_context_quality(self, query: str, context: List[str]) -> float:
        """Assess the quality of retrieved context for the query"""
        if not context:
            return 0.0
        
        query_words = set(query.lower().split())
        
        # Calculate average relevance of context chunks
        relevance_scores = []
        for chunk in context:
            chunk_words = set(chunk.lower().split())
            overlap = len(query_words.intersection(chunk_words))
            relevance = overlap / max(len(query_words), 1)
            relevance_scores.append(relevance)
        
        # Bonus for multiple relevant chunks
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        diversity_bonus = min(0.2, len(context) * 0.05)  # Up to 0.2 bonus
        
        return min(1.0, avg_relevance + diversity_bonus)
    
    def _calculate_confidence_score(self, 
                                   evaluation_scores: Dict[str, float],
                                   context_quality: float,
                                   context_count: int) -> float:
        """Calculate confidence score based on various factors"""
        
        # Base confidence from evaluation scores
        overall_score = evaluation_scores.get('overall', 3.0)
        base_confidence = overall_score / 5.0
        
        # Adjust based on context quality
        context_factor = context_quality * 0.3
        
        # Adjust based on score consistency
        scores = [evaluation_scores.get(key, 3.0) for key in 
                 ['faithfulness', 'relevance', 'completeness', 'clarity']]
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0
        consistency_factor = max(0, 0.2 - score_std * 0.1)  # Lower std = higher confidence
        
        # Adjust based on context availability
        context_availability = min(0.2, context_count * 0.05)
        
        confidence = base_confidence + context_factor + consistency_factor + context_availability
        return min(1.0, max(0.0, confidence))
    
    def _update_quality_trends(self, metrics: AnswerQualityMetrics):
        """Update quality trends based on new metrics"""
        current_time = datetime.now()
        
        # Update hourly trend
        hour_key = current_time.strftime("%Y-%m-%d-%H")
        self._update_trend_period("hour", hour_key, metrics)
        
        # Update daily trend
        day_key = current_time.strftime("%Y-%m-%d")
        self._update_trend_period("day", day_key, metrics)
    
    def _update_trend_period(self, period: str, time_key: str, metrics: AnswerQualityMetrics):
        """Update trend for a specific time period"""
        
        # Find existing trend for this period
        existing_trend = None
        for trend in self.quality_trends:
            if trend.get('period') == period and trend.get('time_key') == time_key:
                existing_trend = trend
                break
        
        if existing_trend:
            # Update existing trend
            total = existing_trend['total_queries']
            new_total = total + 1
            
            # Update running averages
            existing_trend['avg_overall_score'] = (
                (existing_trend['avg_overall_score'] * total + metrics.overall_score) / new_total
            )
            existing_trend['avg_confidence'] = (
                (existing_trend['avg_confidence'] * total + metrics.confidence_score) / new_total
            )
            existing_trend['total_queries'] = new_total
            
            if metrics.overall_score < 2.5:
                existing_trend['low_quality_count'] += 1
                
        else:
            # Create new trend
            new_trend = {
                'period': period,
                'time_key': time_key,
                'avg_overall_score': metrics.overall_score,
                'avg_confidence': metrics.confidence_score,
                'total_queries': 1,
                'low_quality_count': 1 if metrics.overall_score < 2.5 else 0,
                'timestamp': metrics.timestamp
            }
            self.quality_trends.append(new_trend)
        
        # Save updated trends
        self._save_trends()
    
    def get_quality_summary(self, period: str = "day", limit: int = 10) -> Dict[str, Any]:
        """Get quality summary for a specific period"""
        
        # Get recent metrics for backwards compatibility with demo
        recent_metrics = self.get_recent_metrics(limit)
        
        # Calculate statistics from recent metrics
        total_evaluations = len(self.metrics_history)
        recent_evaluations = len(recent_metrics)
        
        if recent_metrics:
            avg_overall_score = sum(m.get('overall_score', 3.0) for m in recent_metrics) / len(recent_metrics)
            avg_confidence = sum(m.get('confidence_score', 0.5) for m in recent_metrics) / len(recent_metrics)
            low_quality_count = sum(1 for m in recent_metrics if m.get('overall_score', 3.0) < 2.5)
        else:
            avg_overall_score = 0.0
            avg_confidence = 0.0
            low_quality_count = 0
        
        # Filter trends by period
        period_trends = [t for t in self.quality_trends if t.get('period') == period]
        period_trends.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        recent_trends = period_trends[:limit] if period_trends else []
        
        # Calculate trend statistics
        trend_total_queries = sum(t.get('total_queries', 0) for t in recent_trends)
        if trend_total_queries > 0:
            weighted_avg_score = sum(
                t.get('avg_overall_score', 0) * t.get('total_queries', 0) 
                for t in recent_trends
            ) / trend_total_queries
            
            weighted_avg_confidence = sum(
                t.get('avg_confidence', 0) * t.get('total_queries', 0) 
                for t in recent_trends
            ) / trend_total_queries
            
            total_low_quality = sum(t.get('low_quality_count', 0) for t in recent_trends)
            quality_rate = ((trend_total_queries - total_low_quality) / trend_total_queries) * 100
        else:
            weighted_avg_score = avg_overall_score
            weighted_avg_confidence = avg_confidence
            quality_rate = ((recent_evaluations - low_quality_count) / max(recent_evaluations, 1)) * 100
        
        return {
            # Backwards compatibility keys for demo
            'total_evaluations': total_evaluations,
            'recent_evaluations': recent_evaluations,
            'avg_overall_score': round(avg_overall_score, 2),
            'avg_confidence': round(avg_confidence, 2),
            'low_quality_count': low_quality_count,
            
            # Standard keys
            'period': period,
            'trends': recent_trends,
            'overall_stats': {
                'avg_score': round(weighted_avg_score, 2),
                'avg_confidence': round(weighted_avg_confidence, 2),
                'total_queries': trend_total_queries,
                'quality_rate': round(quality_rate, 1)
            }
        }
    
    def get_recent_metrics(self, limit: int = 50) -> List[Dict]:
        """Get recent answer metrics"""
        return self.metrics_history[-limit:] if self.metrics_history else []
    
    def check_quality_alerts(self) -> List[Dict[str, Any]]:
        """Check for quality issues that require attention"""
        alerts = []
        
        # Check recent performance
        recent_metrics = self.get_recent_metrics(10)
        if len(recent_metrics) >= 5:
            recent_scores = [m.get('overall_score', 3.0) for m in recent_metrics]
            avg_recent_score = sum(recent_scores) / len(recent_scores)
            
            if avg_recent_score < 2.5:
                alerts.append({
                    'type': 'low_quality',
                    'message': f'Recent average quality score is low: {avg_recent_score:.2f}/5.0',
                    'severity': 'high',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Check for declining trend
            if len(recent_scores) >= 5:
                first_half = recent_scores[:len(recent_scores)//2]
                second_half = recent_scores[len(recent_scores)//2:]
                
                if sum(second_half)/len(second_half) < sum(first_half)/len(first_half) - 0.5:
                    alerts.append({
                        'type': 'declining_quality',
                        'message': 'Quality scores showing declining trend',
                        'severity': 'medium',
                        'timestamp': datetime.now().isoformat()
                    })
        
        # Check confidence scores
        if recent_metrics:
            recent_confidence = [m.get('confidence_score', 0.5) for m in recent_metrics[-5:]]
            avg_confidence = sum(recent_confidence) / len(recent_confidence)
            
            if avg_confidence < 0.3:
                alerts.append({
                    'type': 'low_confidence',
                    'message': f'Recent average confidence is low: {avg_confidence:.2f}',
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts 

# Global answer evaluator instance
_answer_evaluator = None

def get_answer_evaluator() -> AnswerEvaluator:
    """Get global answer evaluator instance"""
    global _answer_evaluator
    if _answer_evaluator is None:
        # Import here to avoid circular imports
        from app.llm.ollama_runner import ollama_runner
        _answer_evaluator = AnswerEvaluator(ollama_runner=ollama_runner)
    return _answer_evaluator 