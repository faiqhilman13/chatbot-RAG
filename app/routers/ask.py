from fastapi import APIRouter, Request, HTTPException
from app.utils.file_loader import get_all_documents
from app.retrievers.rag import rag_retriever
from app.llm.ollama_runner import ollama_runner
from app.config import DOCUMENTS_DIR
import os
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter(tags=["qa"])

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question and get an answer using RAG"""
    question = request.question
    
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Load or build vectorstore
    if not rag_retriever.load_vectorstore():
        # If vectorstore doesn't exist, build it from available documents
        docs = get_all_documents(DOCUMENTS_DIR)
        if not docs:
            return {
                "question": question,
                "answer": "No documents found to answer your question. Please upload some PDF documents first.",
                "sources": []
            }
        
        rag_retriever.build_vectorstore(docs)
    
    # Get the most recent document filename if there are any documents
    from app.main import document_store
    
    most_recent_filename = None
    if document_store:
        # Get the most recent document ID (assuming the latest added is the one we want)
        most_recent_doc = list(document_store.values())[-1]
        most_recent_filename = most_recent_doc.get("filename")
        print(f"[INFO] Using most recent document: {most_recent_filename}")
    
    # Retrieve context, filtered by the most recent document if available
    context, sources = rag_retriever.retrieve_context(
        question=question,
        source_filter=most_recent_filename
    )
    
    if not context:
        return {
            "question": question,
            "answer": "I couldn't find any relevant information to answer your question.",
            "sources": []
        }
    
    # Get answer from LLM
    answer = ollama_runner.get_answer_from_context(question, context)
    
    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }

@router.post("/upload_and_process")
async def upload_and_process(file_path: str):
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