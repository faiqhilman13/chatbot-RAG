"""
Real-Time Performance Monitoring & Analytics Dashboard

This module implements comprehensive performance monitoring for the RAG system,
including query pattern analytics, performance tracking, and alert systems.
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    """Detailed metrics for a single query"""
    query_id: str
    query_text: str
    timestamp: str
    processing_time: float
    retrieval_time: float
    llm_time: float
    total_chunks_retrieved: int
    final_chunks_used: int
    retrieval_method: str
    answer_quality_score: float
    confidence_score: float
    user_feedback: Optional[str] = None
    error_occurred: bool = False
    error_message: Optional[str] = None

@dataclass
class SystemHealthMetrics:
    """Overall system health indicators"""
    timestamp: str
    avg_processing_time: float
    successful_queries: int
    failed_queries: int
    avg_quality_score: float
    avg_confidence_score: float
    memory_usage_mb: float
    cpu_usage_percent: float
    active_sessions: int

@dataclass
class PerformanceAlert:
    """Alert for performance issues"""
    alert_id: str
    alert_type: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    timestamp: str
    metric_value: float
    threshold: float
    resolved: bool = False

class PerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self, 
                 metrics_file: str = "data/query_metrics.json",
                 health_file: str = "data/system_health.json",
                 alerts_file: str = "data/performance_alerts.json",
                 max_metrics_memory: int = 1000):
        """
        Initialize performance monitor
        
        Args:
            metrics_file: File to store query metrics
            health_file: File to store system health metrics
            alerts_file: File to store performance alerts
            max_metrics_memory: Maximum metrics to keep in memory
        """
        self.metrics_file = Path(metrics_file)
        self.health_file = Path(health_file)
        self.alerts_file = Path(alerts_file)
        self.max_metrics_memory = max_metrics_memory
        
        # Create data directory
        self.metrics_file.parent.mkdir(exist_ok=True)
        
        # In-memory storage for real-time monitoring
        self.query_metrics = deque(maxlen=max_metrics_memory)
        self.health_metrics = deque(maxlen=100)  # Keep last 100 health snapshots
        self.active_alerts = []
        
        # Performance thresholds
        self.thresholds = {
            'max_processing_time': 30.0,  # seconds
            'min_quality_score': 2.5,     # 0-5 scale
            'min_confidence_score': 0.3,  # 0-1 scale
            'max_error_rate': 0.1,        # 10%
            'max_memory_usage': 2048,     # MB
            'max_cpu_usage': 80.0,        # percent
        }
        
        # Query pattern tracking
        self.query_patterns = defaultdict(int)
        self.popular_queries = defaultdict(int)
        self.error_patterns = defaultdict(int)
        
        # Real-time metrics
        self.current_sessions = set()
        self.query_times = deque(maxlen=100)  # Last 100 query times
        self.quality_scores = deque(maxlen=100)  # Last 100 quality scores
        
        # Background monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Load existing data
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing metrics and alerts from files"""
        try:
            # Load query metrics
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    stored_metrics = json.load(f)
                    for metric_data in stored_metrics[-self.max_metrics_memory:]:
                        self.query_metrics.append(metric_data)
            
            # Load health metrics
            if self.health_file.exists():
                with open(self.health_file, 'r') as f:
                    stored_health = json.load(f)
                    for health_data in stored_health[-100:]:
                        self.health_metrics.append(health_data)
            
            # Load alerts
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r') as f:
                    self.active_alerts = json.load(f)
                    
        except Exception as e:
            logger.warning(f"Could not load existing monitoring data: {e}")
    
    def _save_metrics(self):
        """Save current metrics to files"""
        try:
            # Save query metrics
            with open(self.metrics_file, 'w') as f:
                json.dump(list(self.query_metrics), f, indent=2)
            
            # Save health metrics
            with open(self.health_file, 'w') as f:
                json.dump(list(self.health_metrics), f, indent=2)
            
            # Save alerts
            with open(self.alerts_file, 'w') as f:
                json.dump(self.active_alerts, f, indent=2)
                
        except Exception as e:
            logger.error(f"Could not save monitoring data: {e}")
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system health metrics
                health_metrics = self._collect_system_health()
                self.health_metrics.append(asdict(health_metrics))
                
                # Check for performance alerts
                self._check_performance_alerts()
                
                # Save metrics periodically
                self._save_metrics()
                
                # Sleep for monitoring interval (30 seconds)
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)
    
    def record_query_metrics(self, metrics: QueryMetrics):
        """Record metrics for a completed query"""
        
        # Add to in-memory storage
        metrics_dict = asdict(metrics)
        self.query_metrics.append(metrics_dict)
        
        # Update real-time tracking
        self.query_times.append(metrics.processing_time)
        self.quality_scores.append(metrics.answer_quality_score)
        
        # Update query patterns
        self._update_query_patterns(metrics)
        
        # Check for immediate alerts
        self._check_query_alerts(metrics)
        
        # Save periodically
        if len(self.query_metrics) % 10 == 0:
            self._save_metrics()
        
        logger.debug(f"Recorded metrics for query {metrics.query_id}")
    
    def _update_query_patterns(self, metrics: QueryMetrics):
        """Update query pattern tracking"""
        
        # Extract query type pattern
        query_lower = metrics.query_text.lower()
        
        if any(word in query_lower for word in ['what', 'explain', 'describe']):
            self.query_patterns['descriptive'] += 1
        elif any(word in query_lower for word in ['who', 'when', 'where']):
            self.query_patterns['factual'] += 1
        elif any(word in query_lower for word in ['how', 'why']):
            self.query_patterns['reasoning'] += 1
        elif any(word in query_lower for word in ['compare', 'difference', 'versus']):
            self.query_patterns['comparative'] += 1
        else:
            self.query_patterns['other'] += 1
        
        # Track popular queries (simplified)
        query_key = metrics.query_text[:50].lower().strip()
        self.popular_queries[query_key] += 1
        
        # Track error patterns
        if metrics.error_occurred:
            error_type = metrics.error_message[:30] if metrics.error_message else "unknown"
            self.error_patterns[error_type] += 1
    
    def _collect_system_health(self) -> SystemHealthMetrics:
        """Collect current system health metrics"""
        import psutil
        
        current_time = datetime.now().isoformat()
        
        # Calculate averages from recent metrics
        recent_metrics = list(self.query_metrics)[-50:]  # Last 50 queries
        
        if recent_metrics:
            avg_processing_time = statistics.mean(
                m['processing_time'] for m in recent_metrics
            )
            successful_queries = sum(1 for m in recent_metrics if not m['error_occurred'])
            failed_queries = len(recent_metrics) - successful_queries
            avg_quality_score = statistics.mean(
                m['answer_quality_score'] for m in recent_metrics
            )
            avg_confidence_score = statistics.mean(
                m['confidence_score'] for m in recent_metrics
            )
        else:
            avg_processing_time = 0.0
            successful_queries = 0
            failed_queries = 0
            avg_quality_score = 0.0
            avg_confidence_score = 0.0
        
        # System resource usage
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
        cpu_usage = psutil.cpu_percent(interval=1)
        
        return SystemHealthMetrics(
            timestamp=current_time,
            avg_processing_time=avg_processing_time,
            successful_queries=successful_queries,
            failed_queries=failed_queries,
            avg_quality_score=avg_quality_score,
            avg_confidence_score=avg_confidence_score,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            active_sessions=len(self.current_sessions)
        )
    
    def _check_query_alerts(self, metrics: QueryMetrics):
        """Check for alerts related to specific query"""
        
        # Processing time alert
        if metrics.processing_time > self.thresholds['max_processing_time']:
            self._create_alert(
                alert_type="slow_query",
                severity="medium",
                message=f"Query took {metrics.processing_time:.2f}s (threshold: {self.thresholds['max_processing_time']}s)",
                metric_value=metrics.processing_time,
                threshold=self.thresholds['max_processing_time']
            )
        
        # Quality score alert
        if metrics.answer_quality_score < self.thresholds['min_quality_score']:
            self._create_alert(
                alert_type="low_quality",
                severity="high",
                message=f"Answer quality score {metrics.answer_quality_score:.2f} below threshold {self.thresholds['min_quality_score']}",
                metric_value=metrics.answer_quality_score,
                threshold=self.thresholds['min_quality_score']
            )
        
        # Confidence score alert
        if metrics.confidence_score < self.thresholds['min_confidence_score']:
            self._create_alert(
                alert_type="low_confidence",
                severity="medium",
                message=f"Answer confidence {metrics.confidence_score:.2f} below threshold {self.thresholds['min_confidence_score']}",
                metric_value=metrics.confidence_score,
                threshold=self.thresholds['min_confidence_score']
            )
    
    def _check_performance_alerts(self):
        """Check for system-wide performance alerts"""
        
        if not self.health_metrics:
            return
        
        latest_health = self.health_metrics[-1]
        
        # Memory usage alert
        memory_mb = latest_health['memory_usage_mb']
        if memory_mb > self.thresholds['max_memory_usage']:
            self._create_alert(
                alert_type="high_memory",
                severity="high",
                message=f"Memory usage {memory_mb:.0f}MB exceeds threshold {self.thresholds['max_memory_usage']}MB",
                metric_value=memory_mb,
                threshold=self.thresholds['max_memory_usage']
            )
        
        # CPU usage alert
        cpu_percent = latest_health['cpu_usage_percent']
        if cpu_percent > self.thresholds['max_cpu_usage']:
            self._create_alert(
                alert_type="high_cpu",
                severity="medium",
                message=f"CPU usage {cpu_percent:.1f}% exceeds threshold {self.thresholds['max_cpu_usage']}%",
                metric_value=cpu_percent,
                threshold=self.thresholds['max_cpu_usage']
            )
        
        # Error rate alert
        if len(self.health_metrics) >= 10:
            recent_health = list(self.health_metrics)[-10:]
            total_queries = sum(h['successful_queries'] + h['failed_queries'] for h in recent_health)
            total_failures = sum(h['failed_queries'] for h in recent_health)
            
            if total_queries > 0:
                error_rate = total_failures / total_queries
                if error_rate > self.thresholds['max_error_rate']:
                    self._create_alert(
                        alert_type="high_error_rate",
                        severity="critical",
                        message=f"Error rate {error_rate:.1%} exceeds threshold {self.thresholds['max_error_rate']:.1%}",
                        metric_value=error_rate,
                        threshold=self.thresholds['max_error_rate']
                    )
    
    def _create_alert(self, 
                     alert_type: str,
                     severity: str,
                     message: str,
                     metric_value: float,
                     threshold: float):
        """Create a new performance alert"""
        
        alert_id = f"{alert_type}_{int(time.time())}"
        alert = PerformanceAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now().isoformat(),
            metric_value=metric_value,
            threshold=threshold,
            resolved=False
        )
        
        # Check if similar alert already exists
        similar_exists = any(
            a['alert_type'] == alert_type and not a['resolved']
            for a in self.active_alerts
        )
        
        if not similar_exists:
            self.active_alerts.append(asdict(alert))
            logger.warning(f"Performance alert created: {alert_type} - {message}")
    
    def get_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive dashboard data for the specified time period"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff_time.isoformat()
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.query_metrics
            if m['timestamp'] >= cutoff_str
        ]
        
        recent_health = [
            h for h in self.health_metrics
            if h['timestamp'] >= cutoff_str
        ]
        
        # Calculate summary statistics
        if recent_metrics:
            total_queries = len(recent_metrics)
            successful_queries = sum(1 for m in recent_metrics if not m['error_occurred'])
            avg_processing_time = statistics.mean(m['processing_time'] for m in recent_metrics)
            avg_quality_score = statistics.mean(m['answer_quality_score'] for m in recent_metrics)
            avg_confidence_score = statistics.mean(m['confidence_score'] for m in recent_metrics)
            
            # Processing time percentiles
            processing_times = [m['processing_time'] for m in recent_metrics]
            p50_time = statistics.median(processing_times)
            
            # Calculate p95 and p99 manually since numpy might not be available
            sorted_times = sorted(processing_times)
            n = len(sorted_times)
            p95_time = sorted_times[int(0.95 * n)] if n > 0 else 0
            p99_time = sorted_times[int(0.99 * n)] if n > 0 else 0
        else:
            total_queries = 0
            successful_queries = 0
            avg_processing_time = 0.0
            avg_quality_score = 0.0
            avg_confidence_score = 0.0
            p50_time = 0.0
            p95_time = 0.0
            p99_time = 0.0
        
        # Query patterns analysis
        recent_query_patterns = dict(self.query_patterns)
        
        # Most popular queries
        popular_queries_list = sorted(
            self.popular_queries.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Active alerts
        active_alerts_list = [a for a in self.active_alerts if not a['resolved']]
        
        # Performance trends (last 24 hours by hour)
        hourly_metrics = defaultdict(list)
        for metric in recent_metrics:
            hour_key = metric['timestamp'][:13]  # YYYY-MM-DDTHH
            hourly_metrics[hour_key].append(metric)
        
        performance_trends = []
        for hour in sorted(hourly_metrics.keys()):
            hour_metrics = hourly_metrics[hour]
            performance_trends.append({
                'hour': hour,
                'query_count': len(hour_metrics),
                'avg_processing_time': statistics.mean(m['processing_time'] for m in hour_metrics),
                'avg_quality_score': statistics.mean(m['answer_quality_score'] for m in hour_metrics),
                'error_count': sum(1 for m in hour_metrics if m['error_occurred'])
            })
        
        return {
            'summary': {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': (successful_queries / total_queries * 100) if total_queries > 0 else 0,
                'avg_processing_time': round(avg_processing_time, 2),
                'avg_quality_score': round(avg_quality_score, 2),
                'avg_confidence_score': round(avg_confidence_score, 2),
                'active_sessions': len(self.current_sessions)
            },
            'performance_metrics': {
                'p50_processing_time': round(p50_time, 2),
                'p95_processing_time': round(p95_time, 2),
                'p99_processing_time': round(p99_time, 2),
            },
            'query_patterns': recent_query_patterns,
            'popular_queries': popular_queries_list,
            'active_alerts': active_alerts_list,
            'performance_trends': performance_trends[-24:],  # Last 24 hours
            'system_health': recent_health[-1] if recent_health else None,
            'error_patterns': dict(self.error_patterns)
        }
    
    def add_session(self, session_id: str):
        """Add an active session"""
        self.current_sessions.add(session_id)
    
    def remove_session(self, session_id: str):
        """Remove an active session"""
        self.current_sessions.discard(session_id)
    
    def resolve_alert(self, alert_id: str):
        """Mark an alert as resolved"""
        for alert in self.active_alerts:
            if alert['alert_id'] == alert_id:
                alert['resolved'] = True
                logger.info(f"Alert {alert_id} marked as resolved")
                break
    
    def get_performance_summary(self, period: str = "1h") -> Dict[str, Any]:
        """Get quick performance summary for specified period"""
        
        if period == "1h":
            hours = 1
        elif period == "24h":
            hours = 24
        elif period == "7d":
            hours = 168
        else:
            hours = 24
        
        dashboard_data = self.get_dashboard_data(hours)
        
        return {
            'period': period,
            'total_queries': dashboard_data['summary']['total_queries'],
            'success_rate': dashboard_data['summary']['success_rate'],
            'avg_response_time': dashboard_data['summary']['avg_processing_time'],
            'avg_quality': dashboard_data['summary']['avg_quality_score'],
            'active_alerts': len(dashboard_data['active_alerts']),
            'system_health': 'healthy' if len(dashboard_data['active_alerts']) == 0 else 'issues'
        }

# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
        _performance_monitor.start_monitoring()
    return _performance_monitor 