"""
Feedback Router

Handles user feedback collection and parameter optimization endpoints.
Allows users to rate answers (👍/👎) and provides feedback analytics.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from app.auth import require_auth
from app.utils.feedback_system import get_feedback_system

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Request/Response Models ---

class FeedbackRequest(BaseModel):
    """Request model for submitting feedback"""
    session_id: str
    query: str
    answer: str
    rating: str  # 'positive' or 'negative'
    retrieval_method: str
    retrieval_k: int
    rerank_threshold: float
    quality_score: Optional[float] = None
    confidence_score: Optional[float] = None
    response_time: Optional[float] = None
    user_comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    """Response model for feedback submission"""
    feedback_id: str
    status: str
    message: str

class ParametersResponse(BaseModel):
    """Response model for optimal parameters"""
    retrieval_k: int
    rerank_threshold: float
    hybrid_weight: float
    quality_threshold: Optional[float] = None

# --- Feedback Endpoints ---

@router.post("/submit", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: str = Depends(require_auth)
):
    """
    Submit user feedback for an answer (👍/👎)
    
    This endpoint allows users to rate RAG answers, which is used to:
    - Automatically adjust retrieval parameters (K, rerank thresholds)
    - Fine-tune system performance based on user satisfaction
    - Track answer quality trends over time
    """
    try:
        # Validate rating
        if feedback.rating not in ['positive', 'negative']:
            raise HTTPException(
                status_code=400, 
                detail="Rating must be 'positive' or 'negative'"
            )
        
        # Get feedback system
        feedback_system = get_feedback_system()
        
        # Log the feedback
        feedback_id = feedback_system.log_feedback(
            session_id=feedback.session_id,
            query=feedback.query,
            answer=feedback.answer,
            rating=feedback.rating,
            retrieval_method=feedback.retrieval_method,
            retrieval_k=feedback.retrieval_k,
            rerank_threshold=feedback.rerank_threshold,
            quality_score=feedback.quality_score,
            confidence_score=feedback.confidence_score,
            response_time=feedback.response_time,
            user_comment=feedback.user_comment
        )
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            status="success",
            message="Feedback submitted successfully. System parameters may be automatically adjusted based on patterns."
        )
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@router.get("/optimal-parameters", response_model=ParametersResponse, tags=["Feedback"])
async def get_optimal_parameters(current_user: str = Depends(require_auth)):
    """
    Get current optimal parameters based on user feedback analysis
    
    Returns the system's current optimal retrieval parameters that have been
    automatically adjusted based on user feedback patterns.
    """
    try:
        feedback_system = get_feedback_system()
        params = feedback_system.get_optimal_parameters()
        
        return ParametersResponse(
            retrieval_k=int(params.get('retrieval_k', 5)),
            rerank_threshold=float(params.get('rerank_threshold', 0.7)),
            hybrid_weight=float(params.get('hybrid_weight', 0.5)),
            quality_threshold=params.get('quality_threshold')
        )
        
    except Exception as e:
        logger.error(f"Error getting optimal parameters: {e}")
        raise HTTPException(status_code=500, detail="Failed to get optimal parameters")

@router.get("/summary", tags=["Feedback"])
async def get_feedback_summary(
    hours: int = 24,
    current_user: str = Depends(require_auth)
):
    """
    Get feedback summary and analytics for the specified time period
    
    Returns statistics about user feedback, parameter adjustments, and system optimization.
    """
    try:
        feedback_system = get_feedback_system()
        summary = feedback_system.get_feedback_summary(hours=hours)
        
        return {
            "status": "success",
            "data": summary,
            "message": f"Feedback summary for last {hours} hours"
        }
        
    except Exception as e:
        logger.error(f"Error getting feedback summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get feedback summary")

@router.get("/entries", tags=["Feedback"])
async def get_feedback_entries(
    limit: int = 50,
    current_user: str = Depends(require_auth)
):
    """
    Get recent feedback entries
    
    Returns a list of recent user feedback entries for analysis and review.
    """
    try:
        feedback_system = get_feedback_system()
        entries = feedback_system.get_feedback_entries(limit=limit)
        
        return {
            "status": "success",
            "data": entries,
            "total": len(entries),
            "message": f"Retrieved {len(entries)} recent feedback entries"
        }
        
    except Exception as e:
        logger.error(f"Error getting feedback entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get feedback entries")

@router.get("/health", tags=["Feedback"])
async def feedback_system_health():
    """
    Get feedback system health status
    
    Returns information about the feedback system's status and configuration.
    """
    try:
        feedback_system = get_feedback_system()
        
        return {
            "status": "success",
            "data": {
                "feedback_entries_count": len(feedback_system.feedback_entries),
                "recent_adjustments_count": len(feedback_system.recent_adjustments),
                "configuration": feedback_system.config,
                "optimal_parameters": feedback_system.optimal_params
            },
            "message": "Feedback system is operational"
        }
        
    except Exception as e:
        logger.error(f"Error checking feedback system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to check feedback system health") 