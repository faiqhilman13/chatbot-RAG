from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
import os
from pathlib import Path
from typing import Optional

# Base directory using pathlib
BASE_DIR = Path(__file__).resolve().parent.parent

# File paths using pathlib
VECTORSTORE_DIR = BASE_DIR / "data" / "vector_store"
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"

# Ensure directories exist using pathlib
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

# Convert back to string for printing if needed, but keep as Path objects for usage
print(f"DOCUMENTS_DIR: {str(DOCUMENTS_DIR)}")
print(f"VECTORSTORE_DIR: {str(VECTORSTORE_DIR)}")
print(f"Both directories exist: {DOCUMENTS_DIR.exists() and VECTORSTORE_DIR.exists()}")

# Embedding Models
EMBEDDING_MODEL: Optional = None
CROSS_ENCODER_MODEL: Optional = None

try:
    # Try to load BGE large model for better embeddings
    try:
        EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
        print("BGE large embedding model loaded successfully")
    except Exception as e:
        print(f"Error loading BGE large model: {str(e)}")
        print("Falling back to all-MiniLM-L6-v2")
        EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("Fallback embedding model loaded successfully")
    
    # Try to load cross-encoder model
    try:
        from sentence_transformers import CrossEncoder
        
        CROSS_ENCODER_MODEL = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        print("Cross-encoder model loaded successfully")
    except Exception as e:
        print(f"Error loading cross-encoder model: {str(e)}")
        CROSS_ENCODER_MODEL = None
        
except Exception as e:
    print(f"Error loading embedding models: {str(e)}")
    # Fallback to HuggingFace embeddings if all else fails
    try:
        EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("Fallback to HuggingFace embedding model successful")
    except Exception as e:
        print(f"Error loading fallback embedding model: {str(e)}")
        EMBEDDING_MODEL = None

# LLM setup - will be initialized on demand with fallback handling
LLM_MODEL_NAME = "llama3:8b"  # Using llama3:8b model

# Ollama API URL
OLLAMA_BASE_URL = "http://localhost:11434"

# Retrieval settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVAL_K = 5  # Final number of documents to retrieve after reranking
RETRIEVAL_CANDIDATES = 20  # Number of initial candidates to retrieve before reranking 