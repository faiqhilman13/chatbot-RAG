# Hybrid Knowledge Graph and RAG Chatbot

## Architecture

The system uses a hybrid approach combining RAG (Retrieval Augmented Generation) for document question answering:

### Components

1. **File Loading Module**
   - PDF document processing
   - Text chunking and metadata extraction
   - Document storage

2. **RAG Retrieval Module**
   - FAISS vector storage
   - Sentence transformer embeddings
   - Semantic similarity search

3. **LLM Integration**
   - Ollama runner for generating responses
   - Fallback mechanisms when Ollama is unavailable
   - Prompt templating

4. **API Layer**
   - FastAPI endpoints
   - Document upload and management
   - Question answering interface

5. **UI Layer**
   - HTML/JS interface
   - Document library management
   - Chat interface

## Project Structure

```
chatbot/
├── app/
│   ├── config.py             # Configuration settings
│   ├── main.py               # FastAPI app and main endpoints
│   ├── utils/
│   │   └── file_loader.py    # PDF processing utilities
│   ├── retrievers/
│   │   └── rag.py            # RAG retrieval system
│   ├── llm/
│   │   └── ollama_runner.py  # LLM integration
│   └── routers/
│       └── ask.py            # QA endpoints
├── data/
│   ├── documents/            # Uploaded PDF storage
│   └── vector_store/         # FAISS vector database
└── requirements.txt          # Project dependencies
```

## Technology Stack

- **Languages**: Python
- **API Framework**: FastAPI
- **Embedding Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store**: FAISS
- **LLM**: Ollama (with fallback mechanisms)
- **Document Processing**: PyPDF
- **Frontend**: HTML, JavaScript, CSS

## Style Guidelines

- PEP8 for Python code
- Google-style docstrings
- Type hints for all functions
- Error handling with graceful fallbacks
- Logging for all operations 