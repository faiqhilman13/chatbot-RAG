from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
import os

# File paths
VECTORSTORE_DIR = "data/vector_store"
DOCUMENTS_DIR = "data/documents"

# Ensure directories exist
os.makedirs(VECTORSTORE_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

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