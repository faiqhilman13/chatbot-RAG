"""
Evaluation router for RAG pipeline performance testing.

This module provides API endpoints to evaluate retrieval accuracy
and answer grounding in the RAG system.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from ..utils.evaluation import recall_at_k, answer_in_context, evaluate_rag_pipeline
from ..retrievers.rag import rag_retriever
from ..llm.ollama_runner import ollama_runner
from ..auth import get_current_user

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()


class RecallTestRequest(BaseModel):
    query: str
    correct_phrase: str
    k: int = 5


class GroundingTestRequest(BaseModel):
    answer: str
    query: str  # To retrieve context documents


class EvaluationTestCase(BaseModel):
    query: str
    expected_phrase: str


class ComprehensiveEvalRequest(BaseModel):
    test_cases: List[EvaluationTestCase]


@router.post("/recall")
async def test_recall(request: RecallTestRequest, user: dict = Depends(get_current_user)):
    """
    Test recall@k for a specific query and expected phrase.
    
    This endpoint evaluates whether the expected phrase appears
    in the top k retrieved documents.
    """
    try:
        logger.info(f"Testing recall@{request.k} for query: {request.query}")
        
        recall_result = recall_at_k(
            query=request.query,
            correct_phrase=request.correct_phrase,
            retriever=rag_retriever,
            k=request.k
        )
        
        return {
            "status": "success",
            "data": {
                "query": request.query,
                "correct_phrase": request.correct_phrase,
                "k": request.k,
                "recall_success": recall_result,
                "message": f"Expected phrase {'found' if recall_result else 'not found'} in top {request.k} documents"
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error in recall test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recall test failed: {str(e)}")


@router.post("/grounding")
async def test_grounding(request: GroundingTestRequest, user: dict = Depends(get_current_user)):
    """
    Test answer grounding by comparing an answer with retrieved context.
    
    This endpoint measures how well an answer is grounded in the
    retrieved context documents.
    """
    try:
        logger.info(f"Testing answer grounding for query: {request.query}")
        
        # Retrieve context documents for the query
        context_docs = rag_retriever.retrieve_context(request.query, k=5)
        
        if not context_docs:
            return {
                "status": "success",
                "data": {
                    "query": request.query,
                    "grounding_score": 0.0,
                    "num_context_docs": 0,
                    "message": "No context documents retrieved"
                },
                "error": None
            }
        
        # Calculate grounding score
        grounding_score = answer_in_context(request.answer, context_docs)
        
        return {
            "status": "success",
            "data": {
                "query": request.query,
                "answer": request.answer,
                "grounding_score": grounding_score,
                "num_context_docs": len(context_docs),
                "message": f"Answer grounding score: {grounding_score:.3f}"
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error in grounding test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Grounding test failed: {str(e)}")


@router.post("/comprehensive")
async def comprehensive_evaluation(request: ComprehensiveEvalRequest, user: dict = Depends(get_current_user)):
    """
    Run comprehensive evaluation on multiple test cases.
    
    This endpoint evaluates both recall and grounding across
    multiple queries to provide overall performance metrics.
    """
    try:
        logger.info(f"Running comprehensive evaluation on {len(request.test_cases)} test cases")
        
        # Convert Pydantic models to dictionaries
        test_cases = [
            {
                "query": case.query,
                "expected_phrase": case.expected_phrase
            }
            for case in request.test_cases
        ]
        
        # Run comprehensive evaluation
        results = evaluate_rag_pipeline(test_cases, rag_retriever, ollama_runner)
        
        return {
            "status": "success",
            "data": {
                "summary": {
                    "total_cases": results["total_cases"],
                    "recall_rate": results["recall_rate"],
                    "average_grounding": results["avg_grounding"]
                },
                "detailed_results": results["detailed_results"],
                "message": f"Evaluated {results['total_cases']} test cases"
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive evaluation failed: {str(e)}")


@router.get("/quick-test")
async def quick_evaluation_test(user: dict = Depends(get_current_user)):
    """
    Run a quick evaluation test with predefined test cases.
    
    This endpoint provides a simple way to test the current
    RAG pipeline performance without custom test cases.
    """
    try:
        logger.info("Running quick evaluation test")
        
        # Predefined test cases for quick testing
        quick_test_cases = [
            {
                "query": "What has Faiq done at PricewaterhouseCoopers?",
                "expected_phrase": "PricewaterhouseCoopers"
            },
            {
                "query": "What is Faiq's experience at PwC?",
                "expected_phrase": "PwC"
            },
            {
                "query": "What did Faiq do at Ernst & Young?",
                "expected_phrase": "Ernst"
            }
        ]
        
        # Run evaluation
        results = evaluate_rag_pipeline(quick_test_cases, rag_retriever, ollama_runner)
        
        # Determine overall assessment
        if results["recall_rate"] >= 0.8 and results["avg_grounding"] >= 0.3:
            assessment = "🚀 Excellent performance!"
        elif results["recall_rate"] >= 0.6 and results["avg_grounding"] >= 0.2:
            assessment = "✅ Good performance"
        elif results["recall_rate"] >= 0.4:
            assessment = "⚠️ Needs improvement"
        else:
            assessment = "❌ Poor performance"
        
        return {
            "status": "success",
            "data": {
                "assessment": assessment,
                "recall_rate": f"{results['recall_rate']:.1%}",
                "average_grounding": f"{results['avg_grounding']:.3f}",
                "detailed_results": results["detailed_results"],
                "recommendations": {
                    "recall": "Adjust keyword overlap threshold or improve chunking" if results["recall_rate"] < 0.6 else "Recall performance is good",
                    "grounding": "Improve prompt engineering or context selection" if results["avg_grounding"] < 0.3 else "Answer grounding is adequate"
                }
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error in quick evaluation test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quick evaluation test failed: {str(e)}")


@router.get("/health")
async def evaluation_health_check():
    """
    Health check for the evaluation system.
    
    This endpoint verifies that the evaluation components
    are working properly.
    """
    try:
        # Test if retriever is working
        test_docs = rag_retriever.retrieve_context("test query", k=1)
        retriever_status = "✅ Working" if test_docs is not None else "❌ Failed"
        
        # Test if LLM is available
        try:
            ollama_status = ollama_runner.check_availability()
            llm_status = "✅ Available" if ollama_status else "❌ Unavailable"
        except:
            llm_status = "❌ Error"
        
        return {
            "status": "success",
            "data": {
                "retriever": retriever_status,
                "llm": llm_status,
                "evaluation_functions": "✅ Loaded",
                "message": "Evaluation system health check completed"
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error in evaluation health check: {str(e)}")
        return {
            "status": "error",
            "data": None,
            "error": f"Health check failed: {str(e)}"
        } 