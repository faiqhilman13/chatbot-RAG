# Hybrid RAG Chatbot Tasks

## Current Tasks

- [x] Set up project structure
- [x] Create basic file loading module
- [x] Create RAG retrieval module
- [x] Create Ollama integration
- [x] Create FastAPI endpoints
- [x] Create HTML/JS interface
- [x] Add error handling for file uploads
- [x] Add document deletion functionality
- [x] Restrict RAG context to uploaded document only
- [ ] Create simplified standalone frontend for better user experience
- [ ] Add support for more document types
- [ ] Add comprehensive logging
- [ ] Add unit tests for all components

## In Progress

- [ ] Create a super basic standalone frontend with:
  - [ ] Clean, minimalist UI for document upload
  - [ ] Simplified chat interface
  - [ ] Mobile-responsive design
  - [ ] Basic error handling and user feedback
- [x] Verify all dependencies are installed correctly
- [x] Test end-to-end functionality with PDF documents
- [x] Test fallback mechanisms when Ollama is unavailable

## Completed Tasks (2023-07-15)

- [x] Create PLANNING.md and TASK.md
- [x] Verify project structure
- [x] Review existing code
- [x] Implement document deletion functionality
- [x] Fix document upload issues
- [x] Implement source filtering for RAG to ensure responses come only from current document

## Notes

- The system should work with or without Ollama being available
- When Ollama is not available, the system will return raw context from retrieved documents
- All errors should be handled gracefully with user-friendly messages
- The new simplified frontend should be separate from the embedded HTML UI for easier maintenance

## Future Enhancements

### Task: Explore Advanced/Novel RAG Techniques
*Goal: Move beyond the standard RAG implementation to potentially improve accuracy, reasoning, or efficiency.*

- [ ] **Subtask:** Research alternative RAG architectures (e.g., ReAct, Self-Correction, Flare).
- [ ] **Subtask:** Investigate different embedding models (e.g., instructor-xl, multilingual models) or fine-tuning `all-MiniLM-L6-v2` on domain-specific data.
- [ ] **Subtask:** Explore advanced retrieval strategies (e.g., implementing BM25 for hybrid search alongside FAISS, adding a re-ranking step with a cross-encoder).
- [ ] **Subtask:** Experiment with different LLM prompting techniques (e.g., few-shot prompting, generated queries, step-back prompting).

### Task: Optimize Deletion Efficiency
*Goal: Replace the "nuke and rebuild" FAISS strategy with a more efficient vector store deletion mechanism.*

- [ ] **Subtask:** Research vector databases with efficient ID-based deletion (e.g., ChromaDB, Qdrant, Weaviate, Milvus) suitable for local/self-hosted deployment.
- [ ] **Subtask:** Evaluate tradeoffs (performance, complexity, resource usage, feature set) of top candidates.
- [ ] **Subtask:** Select and install the chosen vector database.
- [ ] **Subtask:** Refactor `RAGRetriever` (`app/retrievers/rag.py`) to interface with the new DB.
- [ ] **Subtask:** Modify `upload_document` (`app/main.py`) to store chunks with unique, trackable IDs in the new DB.
- [ ] **Subtask:** Modify `delete_document` (`app/main.py`) to use the new DB's API to delete vectors by their IDs (associated with the `doc_id`). Remove the "rebuild" logic.
- [ ] **Subtask:** Ensure `document_index.json` mapping between `doc_id` and vector chunk IDs is handled correctly if needed by the chosen DB.
- [ ] **Subtask:** Test deletion performance and verify correctness (deleted context is no longer retrieved).

### Task: Enhance Scalability & Production Readiness
*Goal: Improve the application's robustness, deployability, and ability to handle more load.*

- [ ] **Subtask: Asynchronous Processing:** Refactor `upload_document` in `app/main.py` to use FastAPI `BackgroundTasks` (or Celery/RQ) for `prepare_documents` and vector store updates, returning an immediate response to the user.
- [ ] **Subtask: Containerization:** Create a `Dockerfile` for the backend application.
- [ ] **Subtask: Containerization:** Create a `docker-compose.yml` to orchestrate the backend, Ollama (optional), and potentially the new vector database.
- [ ] **Subtask: Configuration Management:** Refactor `app/config.py` to load settings from environment variables or a `.env` file using Pydantic Settings.
- [ ] **Subtask: Robust Error Handling:** Add more specific `try...except` blocks around I/O operations, API calls (Ollama), and database interactions. Implement more informative logging.
- [ ] **Subtask: API Concurrency:** Research and potentially configure multiple worker processes for the ASGI server (e.g., Uvicorn/Gunicorn workers) if benchmarks indicate CPU-bound limits.
- [ ] **Subtask: Monitoring:** Add a basic health check endpoint (`/health`) that verifies connectivity to the vector DB and Ollama (if configured). 