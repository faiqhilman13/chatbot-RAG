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
   - Source filtering to restrict context to current document

3. **LLM Integration**
   - Ollama runner for generating responses
   - Fallback mechanisms when Ollama is unavailable
   - Prompt templating

4. **API Layer**
   - FastAPI endpoints
   - Document upload and management
   - Question answering interface
   - Document deletion

5. **UI Layer**
   - Embedded HTML/JS interface in the FastAPI app
   - Document library management
   - Chat interface
   - Delete functionality for documents

6. **Standalone Frontend (Planned)**
   - Simple, clean HTML/CSS/JS interface
   - Mobile-responsive design
   - Improved user experience
   - Better error handling and user feedback

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
├── frontend/                 # Standalone frontend (planned)
│   ├── index.html            # Main frontend page
│   ├── css/                  # Stylesheets
│   │   └── style.css         # Main stylesheet
│   └── js/                   # JavaScript files
│       └── app.js            # Frontend logic
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
- **Frontend Framework**: None (vanilla JS for simplicity)

## Style Guidelines

- PEP8 for Python code
- Google-style docstrings
- Type hints for all functions
- Error handling with graceful fallbacks
- Logging for all operations
- Clean, minimalist UI for frontend
- Mobile-first responsive design

## Standalone Frontend Design

The standalone frontend will be a simple, clean interface that allows users to:

1. Upload PDF documents
2. View a list of uploaded documents
3. Delete documents when no longer needed
4. Ask questions about the uploaded documents
5. View answers with source information

The design will prioritize simplicity, usability, and responsiveness across devices.

## Future Improvements / Next Steps

Based on the current implementation, several areas offer potential for significant technical enhancement:

1.  **Explore Advanced/Novel Techniques:** Move beyond the standard RAG pattern by investigating:
    *   Alternative RAG architectures (e.g., ReAct, Self-Correction).
    *   Different or fine-tuned embedding models.
    *   Advanced retrieval strategies (hybrid search, re-ranking).
    *   More sophisticated LLM prompting techniques.

2.  **Optimize Deletion Efficiency:** Replace the current "nuke and rebuild" FAISS strategy:
    *   Research and select a vector database with efficient, built-in ID-based deletion (e.g., ChromaDB, Qdrant, Weaviate, Milvus, potentially self-hosted).
    *   Migrate the vector store implementation, including refactoring upload/deletion logic to use the new database's API.

3.  **Enhance Scalability & Production Readiness:** Prepare the application for potentially larger scale or more robust deployment:
    *   Implement asynchronous processing for document uploads/embeddings.
    *   Containerize the application (Docker/Docker Compose).
    *   Improve configuration management.
    *   Add more comprehensive error handling and logging.
    *   Address potential concurrency bottlenecks.
    *   Integrate basic monitoring. 