# Hybrid RAG Chatbot Tasks

## Current Tasks (2024-07)

- [ ] **Improve RAG Accuracy**
  - [ ] Replace embedding model with mxbai-embed-large
  - [ ] Implement cross-encoder reranking
  - [ ] Benchmark and evaluate performance improvements
- [ ] **Frontend Improvements**
  - [x] Integrate Stagewise toolbar for AI-powered UI editing
  - [x] Reduce visual intensity of UI elements (scrollbar and heading glow effects)
  - [ ] Create simplified standalone frontend with clean, minimalist UI
  - [ ] Implement mobile-responsive design
  - [ ] Add better error handling and user feedback
- [ ] **Code Quality & Testing**
  - [ ] Add comprehensive logging
  - [ ] Add unit tests for all components
  - [ ] Implement full vector deletion logic for FAISS on document removal
- [ ] **Feature Expansion**
  - [ ] Add support for more document types (beyond PDF)

## In Progress

- [ ] Implement advanced embedding model and reranking
- [ ] Test end-to-end functionality with improved RAG pipeline

## Completed Tasks

### 2024-07-17
- [x] Integrate Stagewise toolbar for AI-powered UI editing
- [x] Fix ReactPlugin integration issue
- [x] Reduce scrollbar glow effect for better visual comfort
- [x] Reduce heading glow effect for more subtle UI

### 2023-07-15
- [x] Create PLANNING.md and TASK.md
- [x] Verify project structure
- [x] Review existing code
- [x] Implement document deletion functionality
- [x] Fix document upload issues
- [x] Implement source filtering for RAG to ensure responses come only from current document

### Initial Development
- [x] Set up project structure
- [x] Create basic file loading module
- [x] Create RAG retrieval module
- [x] Create Ollama integration
- [x] Create FastAPI endpoints
- [x] Create HTML/JS interface
- [x] Add error handling for file uploads
- [x] Add document deletion functionality
- [x] Restrict RAG context to uploaded document only
- [x] Verify all dependencies are installed correctly
- [x] Test end-to-end functionality with PDF documents
- [x] Test fallback mechanisms when Ollama is unavailable

## System Requirements

- The system should work with or without Ollama being available
- When Ollama is not available, the system will return raw context from retrieved documents
- All errors should be handled gracefully with user-friendly messages
- The new simplified frontend should be separate from the embedded HTML UI for easier maintenance

## Future Enhancements

### Task: Explore Additional Advanced RAG Techniques
*Goal: Further improve RAG implementation for better accuracy, reasoning, or efficiency.*

- [ ] **Subtask:** Research alternative RAG architectures (e.g., ReAct, Self-Correction, Flare)
- [ ] **Subtask:** Implement hybrid search combining dense and sparse retrievers (e.g., BM25 + embeddings)
- [ ] **Subtask:** Experiment with different LLM prompting techniques (e.g., few-shot prompting, generated queries, step-back prompting)

### Task: Optimize Deletion Efficiency
*Goal: Replace the "nuke and rebuild" FAISS strategy with a more efficient vector store deletion mechanism.*

- [ ] **Subtask:** Research vector databases with efficient ID-based deletion (e.g., ChromaDB, Qdrant, Weaviate, Milvus) suitable for local/self-hosted deployment
- [ ] **Subtask:** Evaluate tradeoffs (performance, complexity, resource usage, feature set) of top candidates
- [ ] **Subtask:** Select and install the chosen vector database
- [ ] **Subtask:** Refactor `RAGRetriever` (`app/retrievers/rag.py`) to interface with the new DB
- [ ] **Subtask:** Modify `upload_document` (`app/main.py`) to store chunks with unique, trackable IDs in the new DB
- [ ] **Subtask:** Modify `delete_document` (`app/main.py`) to use the new DB's API to delete vectors by their IDs (associated with the `doc_id`)
- [ ] **Subtask:** Ensure `document_index.json` mapping between `doc_id` and vector chunk IDs is handled correctly if needed by the chosen DB
- [ ] **Subtask:** Test deletion performance and verify correctness (deleted context is no longer retrieved)

### Task: Enhance Scalability & Production Readiness
*Goal: Improve the application's robustness, deployability, and ability to handle more load.*

- [ ] **Subtask:** Refactor `upload_document` in `app/main.py` to use FastAPI `BackgroundTasks` for asynchronous processing
- [ ] **Subtask:** Create a `Dockerfile` for the backend application
- [ ] **Subtask:** Create a `docker-compose.yml` to orchestrate the backend, Ollama, and vector database
- [ ] **Subtask:** Refactor `app/config.py` to load settings from environment variables or a `.env` file using Pydantic Settings
- [ ] **Subtask:** Add more specific error handling around I/O operations, API calls, and database interactions
- [ ] **Subtask:** Research and configure multiple worker processes for the ASGI server if needed
- [ ] **Subtask:** Add a comprehensive health check endpoint that verifies connectivity to all dependencies 