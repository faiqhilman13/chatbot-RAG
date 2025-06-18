from fastapi import APIRouter, Request, HTTPException, Depends
from app.utils.file_loader import get_all_documents
from app.retrievers.rag import rag_retriever
from app.llm.ollama_runner import ollama_runner
from app.config import DOCUMENTS_DIR
from app.auth import require_auth
from app.utils.feedback_system import get_feedback_system
from app.utils.performance_monitor import get_performance_monitor, QueryMetrics
from app.utils.answer_evaluator import get_answer_evaluator
import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from langchain.schema import Document
import re
import uuid
import time
from datetime import datetime

router = APIRouter(tags=["qa"])

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    doc_filter: Optional[Dict[str, Any]] = None
    
    @validator('question')
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        
        # Basic XSS protection - remove potentially dangerous characters
        dangerous_patterns = [
            r'<script.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Question contains invalid content')
        
        return v.strip()
    
    @validator('doc_filter')
    def validate_doc_filter(cls, v):
        if v is not None:
            # Ensure doc_filter is a dictionary with string keys
            if not isinstance(v, dict):
                raise ValueError('doc_filter must be a dictionary')
            
            for key, value in v.items():
                if not isinstance(key, str):
                    raise ValueError('doc_filter keys must be strings')
                if len(key) > 100:
                    raise ValueError('doc_filter keys too long')
        
        return v

class SourceDocument(BaseModel):
    source: Optional[str] = None
    title: Optional[str] = None
    page: Optional[int] = None

class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceDocument]
    session_id: str = Field(..., description="Session ID for feedback tracking")
    retrieval_method: str = Field(..., description="Retrieval method used")
    retrieval_k: int = Field(..., description="K value used for retrieval")
    rerank_threshold: float = Field(..., description="Reranker threshold used")
    quality_score: Optional[float] = Field(None, description="Answer quality score")
    confidence_score: Optional[float] = Field(None, description="Answer confidence score")
    response_time: Optional[float] = Field(None, description="Total response time in seconds")

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(question_request: QuestionRequest, current_user: str = Depends(require_auth)):
    """Ask a question and get an answer using RAG"""
    # Generate session ID and query ID for tracking
    session_id = str(uuid.uuid4())
    query_id = f"query_{int(time.time())}_{session_id[:8]}"
    
    # Get monitoring instances
    performance_monitor = get_performance_monitor()
    answer_evaluator = get_answer_evaluator()
    
    # Get optimal parameters from feedback system
    feedback_system = get_feedback_system()
    optimal_params = feedback_system.get_optimal_parameters()
    
    # Use validated Pydantic model instead of raw JSON
    question = question_request.question
    doc_filter = question_request.doc_filter
    
    # Start timing
    start_time = time.time()
    error_occurred = False
    error_message = None
    
    try:
        # Track session
        performance_monitor.add_session(session_id)
        
        if not rag_retriever.load_vectorstore():
            error_message = "Vector store not initialized"
            error_occurred = True
            return QuestionResponse(
                question=question,
                answer="Vector store not initialized. Please upload documents first.",
                sources=[],
                session_id=session_id,
                retrieval_method="none",
                retrieval_k=0,
                rerank_threshold=0.0,
                response_time=time.time() - start_time
            )
            
        print(f"[INFO] Retrieving context for question: '{question}' (filter: {doc_filter})")
        print(f"[INFO] Using optimal parameters: K={optimal_params.get('retrieval_k', 5)}, threshold={optimal_params.get('rerank_threshold', 0.7)}")
        
        # Use the new filtering capabilities with optimal parameters
        retrieval_start = time.time()
        relevant_docs: List[Document] = rag_retriever.retrieve_context(
            question=question,
            filter_criteria=doc_filter,
            auto_filter=True,  # Enable automatic filtering
            top_k=optimal_params.get('retrieval_k', 5),  # Use optimal K from feedback
            rerank_threshold=optimal_params.get('rerank_threshold', 0.7)  # Use optimal threshold
        )
        retrieval_time = time.time() - retrieval_start
        
        # Determine retrieval method used
        retrieval_method = getattr(rag_retriever, '_last_retrieval_method', 'hybrid')
        
        print(f"[DEBUG] Retrieved {len(relevant_docs)} chunks. Details:")
        if relevant_docs:
            for i, doc in enumerate(relevant_docs):
                source = doc.metadata.get("source", "N/A")
                title = doc.metadata.get("title", "N/A")
                page = doc.metadata.get("page", "N/A")
                content_snippet = doc.page_content[:100].replace("\n", " ") + "..."
                print(f"  - Chunk {i}: Source='{source}', Title='{title}', Page={page}, Content='{content_snippet}'")
        else:
            print("  - No relevant chunks found.")
        
        if not relevant_docs:
            return QuestionResponse(
                question=question,
                answer="I couldn't find any relevant information to answer your question.",
                sources=[],
                session_id=session_id,
                retrieval_method=retrieval_method,
                retrieval_k=optimal_params.get('retrieval_k', 5),
                rerank_threshold=optimal_params.get('rerank_threshold', 0.7),
                response_time=time.time() - start_time
            )
        
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        formatted_sources = [
            SourceDocument(
                source=doc.metadata.get("source"),
                title=doc.metadata.get("title"),
                page=doc.metadata.get("page")
            ) 
            for doc in relevant_docs
        ]

        print(f"[INFO] Sending question and context to LLM.")
        
        llm_start = time.time()
        answer = ollama_runner.get_answer_from_context(question, context, relevant_docs)
        llm_time = time.time() - llm_start
        total_time = time.time() - start_time
        
        print(f"[INFO] Received answer from LLM. Total time: {total_time:.2f}s")
        
        # Evaluate answer quality using the answer evaluator
        try:
            evaluation_result = answer_evaluator.evaluate_answer_quality(
                query=question,
                answer=answer,
                context=[doc.page_content for doc in relevant_docs],
                processing_time=total_time
            )
            quality_score = evaluation_result.overall_score
            confidence_score = evaluation_result.confidence_score
        except Exception as eval_error:
            print(f"[WARNING] Answer evaluation failed: {eval_error}")
            quality_score = 3.0  # Default neutral score
            confidence_score = 0.8  # Default confidence
        
        # Create monitoring metrics
        query_metrics = QueryMetrics(
            query_id=query_id,
            query_text=question,
            timestamp=datetime.now().isoformat(),
            processing_time=total_time,
            retrieval_time=retrieval_time,
            llm_time=llm_time,
            total_chunks_retrieved=len(relevant_docs),
            final_chunks_used=len(relevant_docs),
            retrieval_method=retrieval_method,
            answer_quality_score=quality_score,
            confidence_score=confidence_score,
            error_occurred=error_occurred,
            error_message=error_message
        )
        
        # Record metrics in monitoring system
        performance_monitor.record_query_metrics(query_metrics)
        
        return QuestionResponse(
            question=question,
            answer=answer,
            sources=formatted_sources,
            session_id=session_id,
            retrieval_method=retrieval_method,
            retrieval_k=optimal_params.get('retrieval_k', 5),
            rerank_threshold=optimal_params.get('rerank_threshold', 0.7),
            quality_score=quality_score,
            confidence_score=confidence_score,
            response_time=total_time
        )
        
    except Exception as e:
        error_occurred = True
        error_message = str(e)
        total_time = time.time() - start_time
        
        print(f"[ERROR] Query processing failed: {e}")
        
        # Still record metrics for failed queries
        try:
            query_metrics = QueryMetrics(
                query_id=query_id,
                query_text=question,
                timestamp=datetime.now().isoformat(),
                processing_time=total_time,
                retrieval_time=0.0,
                llm_time=0.0,
                total_chunks_retrieved=0,
                final_chunks_used=0,
                retrieval_method="error",
                answer_quality_score=0.0,
                confidence_score=0.0,
                error_occurred=True,
                error_message=error_message
            )
            performance_monitor.record_query_metrics(query_metrics)
        except Exception as metric_error:
            print(f"[ERROR] Failed to record error metrics: {metric_error}")
        
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
        
    finally:
        # Clean up session tracking
        performance_monitor.remove_session(session_id)

@router.post("/upload_and_process")
async def upload_and_process(file_path: str, current_user: str = Depends(require_auth)):
    """Add a document to the vectorstore from a path"""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    from app.utils.file_loader import prepare_documents
    
    docs = prepare_documents(file_path)
    if not docs:
        raise HTTPException(status_code=400, detail="Failed to extract text from the document")
    
    # Make sure vectorstore is loaded
    rag_retriever.load_vectorstore()
    
    # Add document to vectorstore
    existing_docs = True if rag_retriever.vectorstore else False
    
    if existing_docs:
        # If vectorstore exists, add to it
        for doc in docs:
            rag_retriever.vectorstore.add_documents([doc])
        rag_retriever.save_vectorstore()
    else:
        # If vectorstore doesn't exist, build it
        rag_retriever.build_vectorstore(docs)
    
    return {
        "message": f"Document processed and added to vectorstore: {file_path}",
        "chunks_count": len(docs)
    } 