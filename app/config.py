from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# File paths
VECTORSTORE_DIR = os.path.abspath(os.path.join(BASE_DIR, "data/vector_store"))
DOCUMENTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "data/documents"))

# Ensure directories exist
os.makedirs(VECTORSTORE_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

print(f"DOCUMENTS_DIR: {DOCUMENTS_DIR}")
print(f"VECTORSTORE_DIR: {VECTORSTORE_DIR}")
print(f"Both directories exist: {os.path.exists(DOCUMENTS_DIR) and os.path.exists(VECTORSTORE_DIR)}")

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