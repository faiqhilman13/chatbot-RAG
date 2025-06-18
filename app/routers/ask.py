from fastapi import APIRouter, Request, HTTPException, Depends
from app.utils.file_loader import get_all_documents
from app.retrievers.rag import rag_retriever
from app.llm.ollama_runner import ollama_runner
from app.config import DOCUMENTS_DIR
from app.auth import require_auth
import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from langchain.schema import Document
import re

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

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(question_request: QuestionRequest, current_user: str = Depends(require_auth)):
    """Ask a question and get an answer using RAG"""
    # Use validated Pydantic model instead of raw JSON
    question = question_request.question
    doc_filter = question_request.doc_filter
    
    if not rag_retriever.load_vectorstore():
        return QuestionResponse(
            question=question,
            answer="Vector store not initialized. Please upload documents first.",
            sources=[]
        )
        
    print(f"[INFO] Retrieving context for question: '{question}' (filter: {doc_filter})")
    
    # Use the new filtering capabilities
    relevant_docs: List[Document] = rag_retriever.retrieve_context(
        question=question,
        filter_criteria=doc_filter,
        auto_filter=True  # Enable automatic filtering
    )
    
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
            sources=[]
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
    answer = ollama_runner.get_answer_from_context(question, context)
    print(f"[INFO] Received answer from LLM.")
    
    return QuestionResponse(
        question=question,
        answer=answer,
        sources=formatted_sources
    )

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