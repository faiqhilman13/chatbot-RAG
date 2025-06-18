"""
API endpoints for performance monitoring and answer evaluation
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any, List
from app.auth import require_auth
from app.utils.performance_monitor import get_performance_monitor
from app.utils.answer_evaluator import AnswerEvaluator
from app.llm.ollama_runner import ollama_runner

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard(hours: int = 24, user: dict = Depends(require_auth)):
    """Get comprehensive dashboard data for monitoring"""
    try:
        performance_monitor = get_performance_monitor()
        dashboard_data = performance_monitor.get_dashboard_data(hours=hours)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

@router.get("/performance/summary")
async def get_performance_summary(period: str = "24h", user: dict = Depends(require_auth)):
    """Get quick performance summary"""
    try:
        performance_monitor = get_performance_monitor()
        summary = performance_monitor.get_performance_summary(period=period)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching performance summary: {str(e)}")

@router.get("/quality/summary")
async def get_quality_summary(user: dict = Depends(require_auth)):
    """Get answer quality summary"""
    try:
        answer_evaluator = ollama_runner.answer_evaluator
        quality_summary = answer_evaluator.get_quality_summary()
        return quality_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quality summary: {str(e)}")

@router.get("/quality/recent")
async def get_recent_quality_metrics(limit: int = 50, user: dict = Depends(require_auth)):
    """Get recent answer quality metrics"""
    try:
        answer_evaluator = ollama_runner.answer_evaluator
        recent_metrics = answer_evaluator.get_recent_metrics(limit=limit)
        return {"metrics": recent_metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent metrics: {str(e)}")

@router.post("/evaluate")
async def evaluate_answer(
    query: str,
    answer: str,
    context: List[str],
    user: dict = Depends(require_auth)
):
    """Manually evaluate an answer using LLM-as-a-Judge"""
    try:
        answer_evaluator = ollama_runner.answer_evaluator
        quality_metrics = answer_evaluator.evaluate_answer_quality(
            query=query,
            answer=answer,
            context=context
        )
        
        return {
            "evaluation": {
                "faithfulness_score": quality_metrics.faithfulness_score,
                "relevance_score": quality_metrics.relevance_score,
                "completeness_score": quality_metrics.completeness_score,
                "clarity_score": quality_metrics.clarity_score,
                "overall_score": quality_metrics.overall_score,
                "confidence_score": quality_metrics.confidence_score,
                "context_quality": quality_metrics.context_quality
            },
            "timestamp": quality_metrics.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answer: {str(e)}")

@router.get("/system/health")
async def get_system_health(user: dict = Depends(require_auth)):
    """Get current system health status"""
    try:
        performance_monitor = get_performance_monitor()
        
        # Get recent dashboard data
        dashboard_data = performance_monitor.get_dashboard_data(hours=1)
        summary = dashboard_data.get('summary', {})
        
        # Determine overall health
        success_rate = summary.get('success_rate', 0)
        avg_response_time = summary.get('avg_processing_time', 0)
        avg_quality = summary.get('avg_quality_score', 0)
        
        if success_rate >= 95 and avg_response_time <= 10 and avg_quality >= 3.5:
            health_status = "excellent"
        elif success_rate >= 90 and avg_response_time <= 20 and avg_quality >= 3.0:
            health_status = "good"
        elif success_rate >= 80 and avg_response_time <= 30 and avg_quality >= 2.5:
            health_status = "fair"
        else:
            health_status = "poor"
        
        return {
            "health_status": health_status,
            "metrics": {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "avg_quality_score": avg_quality,
                "total_queries": summary.get('total_queries', 0),
                "active_sessions": summary.get('active_sessions', 0)
            },
            "timestamp": dashboard_data.get('performance_trends', [{}])[-1].get('hour', 'unknown') if dashboard_data.get('performance_trends') else 'unknown'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system health: {str(e)}")

@router.get("/patterns/queries")
async def get_query_patterns(hours: int = 24, user: dict = Depends(require_auth)):
    """Get query pattern analytics"""
    try:
        performance_monitor = get_performance_monitor()
        dashboard_data = performance_monitor.get_dashboard_data(hours=hours)
        
        return {
            "query_patterns": dashboard_data.get('query_patterns', {}),
            "popular_queries": dashboard_data.get('popular_queries', []),
            "error_patterns": dashboard_data.get('error_patterns', {}),
            "period_hours": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching query patterns: {str(e)}")

@router.get("/trends/performance")
async def get_performance_trends(hours: int = 24, user: dict = Depends(require_auth)):
    """Get performance trends over time"""
    try:
        performance_monitor = get_performance_monitor()
        dashboard_data = performance_monitor.get_dashboard_data(hours=hours)
        
        return {
            "trends": dashboard_data.get('performance_trends', []),
            "period_hours": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching performance trends: {str(e)}") 