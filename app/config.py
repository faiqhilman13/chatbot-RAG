from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
import os
from pathlib import Path

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

# Models
try:
    EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("Embedding model loaded successfully")
except Exception as e:
    print(f"Error loading embedding model: {str(e)}")
    EMBEDDING_MODEL = None

# LLM setup - will be initialized on demand with fallback handling
LLM_MODEL_NAME = "mistral"  # Can be changed to "llama3" or others

# Ollama API URL
OLLAMA_BASE_URL = "http://localhost:11434"

# Retrieval settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVAL_K = 5  # Number of documents to retrieve 