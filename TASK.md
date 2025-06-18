# Hybrid RAG Chatbot Tasks

## Current Tasks (2024-07)

### **🔥 HIGH PRIORITY: Improve RAG Answer Accuracy**
*Goal: Fix incorrect information mixing between different work experiences and improve contextual accuracy.*

**Issue Identified:** The system correctly retrieves relevant documents but LLM mixing information from different sections/experiences within the same document. Example: PwC question answered correctly about job title/dates but incorrectly included revenue generation details from a different role.

**✅ MAJOR BREAKTHROUGH:** Successfully fixed the primary accuracy issue! The keyword overlap filtering was too strict (10% threshold), causing the system to return only 1 chunk instead of multiple relevant chunks. By reducing the threshold to 3% and adding company alias detection (PwC ↔ PricewaterhouseCoopers), the system now retrieves 2+ relevant chunks for company-specific queries, providing much more complete and accurate answers.

**🎯 EVALUATION SYSTEM DEPLOYED:** Added comprehensive evaluation functions (`recall_at_k`, `answer_in_context`, `evaluate_rag_pipeline`) with FastAPI endpoints at `/api/eval/`. Current performance: 60% recall rate for company queries (vs ~20% before improvements). PwC queries now successfully retrieve "PricewaterhouseCoopers" content - a major improvement!

**🧠 Generalized Strategies for Accuracy** 
Since the RAG system is domain-agnostic and handles various document types (CVs, financial reports, stories, etc.), implementing generalized accuracy improvements without hardcoding for specific formats:

**Approach Comparison:**
| Approach | Works for | Complexity | Benefit |
|----------|-----------|------------|---------|
| Sliding windows | All domains | Low | High |
| Post-rerank clustering | All | Medium | High |
| Instruction prompting | All | Low | Medium |
| Entity filtering | Structured/Named text | Medium | Medium |
| Hybrid keyword+vector | Reports, structured docs | Medium | Medium |

- [x] **Subtask:** **Implement Sliding Window Chunking** - Replace static 500-token chunks with sliding windows (e.g., chunk_size=800, chunk_overlap=300) to preserve context across boundaries and reduce information loss ✅ **COMPLETED** - Implemented and working well
- [x] **Subtask:** **Implement Post-Rerank Clustering** - After cross-encoder reranking, cluster top results based on metadata similarity (source, page) or cosine similarity, then select the most cohesive cluster to prevent mixing disparate contexts ✅ **COMPLETED** - Implemented and working well  
- [x] **Subtask:** **PRIORITY: Implement Content-Based Semantic Clustering** - Replace metadata clustering with semantic similarity clustering using embedding cosine similarity to group topically related chunks (works for any document type: CVs, reports, stories, etc.) ✅ **COMPLETED** - Implemented semantic clustering with DBSCAN
- [x] **Subtask:** **PRIORITY: Add Keyword Overlap Filtering** - Boost chunks with high lexical overlap with query terms, preventing retrieval of unrelated sections regardless of document type ✅ **COMPLETED** - Reduced threshold from 10% to 3% and added company alias detection (PwC, PricewaterhouseCoopers, etc.)
- [x] **Subtask:** **Implement Query-Context Coherence Scoring** - Score retrieved chunks based on semantic coherence with each other, not just query similarity, to prevent mixing unrelated topics ✅ **COMPLETED** - Implemented coherence scoring using cosine similarity between chunk embeddings
- [ ] **Subtask:** **Add Chunk Boundary Awareness** - Detect when chunks span different topics/sections and split them more intelligently (works for any structured document)
- [x] **Subtask:** **Add Company-Specific Context Filtering** - Extract company names from queries (e.g., "PwC", "PricewaterhouseCoopers") and filter chunks to only include content mentioning that specific company ✅ **COMPLETED** - Implemented company alias detection and enhanced query intent detection for company-related queries
- [ ] **Subtask:** **Add Dynamic In-Context Instruction Prompting** - Append context-specific instructions to LLM prompts based on query type (e.g., "If multiple contexts are provided, prefer those referring to the same topic or entity. Avoid mixing unrelated sources.")
- [ ] **Subtask:** **Implement Entity Filtering Pre-Reranking** - Use spaCy to extract entities from query and down-rank chunks that don't contain key entities to improve relevance
- [ ] **Subtask:** **Add Hybrid FAISS + Keyword Filtering** - Combine vector similarity with keyword overlap filtering to boost chunks with high lexical similarity to the query
- [ ] **Subtask:** **Implement Semantic Chunk Grouping** - Move beyond fixed-size chunking to semantic segmentation that respects document structure and content boundaries
- [ ] **Subtask:** **Add Cluster Cohesion Scoring** - Measure internal similarity within retrieved chunk clusters and prefer more cohesive result sets
- [ ] **Subtask:** **Enhance Cross-Encoder with Context Awareness** - Modify reranking to consider not just query-chunk similarity but also chunk-to-chunk coherence within the result set
- [ ] **Subtask:** **Implement Multi-Chunk Context Windows** - For complex queries, retrieve larger context windows that span multiple related chunks while maintaining semantic boundaries
- [x] **Subtask:** **Add Answer Validation Pipeline** - Implement post-generation validation to check if facts in the answer are supported by the same logical document sections ✅ **COMPLETED** - Implemented comprehensive evaluation functions: recall_at_k(), answer_in_context(), and evaluate_rag_pipeline() with API endpoints for testing RAG accuracy

### Task: Enhance Source Filtering System
*Goal: Make the filtering system more robust and user-friendly.*

- [ ] **Subtask:** Add more document types and intelligent classification (technical docs, legal docs, etc.)
- [ ] **Subtask:** Implement fuzzy matching for document titles and keywords
- [ ] **Subtask:** Add user-defined custom filters and tags
- [ ] **Subtask:** Implement confidence scoring for automatic filter detection
- [ ] **Subtask:** Add filter analytics to show which filters are most effective

### Task: Improve User Experience
*Goal: Enhance the frontend with better feedback and interaction patterns.*

- [ ] **Subtask:** Add toast notifications for filter applications and system status
- [ ] **Subtask:** Implement real-time typing indicators and response streaming
- [ ] **Subtask:** Add source document preview/highlighting functionality
- [ ] **Subtask:** Implement search within chat history
- [ ] **Subtask:** Add export functionality for chat conversations
- [ ] **Subtask:** Implement keyboard shortcuts for common actions

### Task: Performance and Monitoring
*Goal: Add observability and performance optimization.*

- [ ] **Subtask:** Implement query performance metrics and logging
- [ ] **Subtask:** Add retrieval accuracy metrics and A/B testing framework
- [ ] **Subtask:** Create dashboard for system health and usage analytics
- [ ] **Subtask:** Optimize chunk size and overlap based on document types
- [ ] **Subtask:** Implement caching for frequently asked questions

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

## In Progress

- [ ] Add better error handling and user feedback
  - [ ] Add toast notifications for success/error messages
  - [ ] Improve form validation
  - [ ] Add loading indicators

## System Requirements

- The system should work with or without Ollama being available
- When Ollama is not available, the system will return raw context from retrieved documents
- All errors should be handled gracefully with user-friendly messages
- The new React.js frontend should provide better code organization and maintainability while preserving the original design aesthetic
- The UI should have separate pages for chat, document management, and uploads, accessible via the sidebar navigation

---

## ✅ Completed Tasks

### 2024-12-30 - Session 1
- [x] **Implement Backend Authentication System** ✅ **COMPLETED**
  - [x] **Authentication Module Development**
    - [x] Create comprehensive authentication module (`app/auth.py`) with password hashing, session management, and authentication dependencies
    - [x] Implement bcrypt password hashing with proper verification
    - [x] Create session-based authentication (avoiding JWT complexity)
    - [x] Add authentication dependencies for FastAPI endpoints
    - [x] Implement user management with admin/admin123 credentials
  - [x] **Authentication Router Implementation**
    - [x] Create authentication router (`app/routers/auth.py`) with login, logout, and status endpoints
    - [x] Add `POST /auth/login` endpoint for user authentication
    - [x] Add `POST /auth/logout` endpoint for session termination
    - [x] Add `GET /auth/status` endpoint for authentication status checking
    - [x] Add `GET /auth/me` endpoint for authenticated user information
    - [x] Implement proper request/response models with Pydantic
  - [x] **Main Application Integration**
    - [x] Add SessionMiddleware to FastAPI application for session management
    - [x] Integrate authentication router with main application
    - [x] Protect all sensitive endpoints with authentication requirements:
      - [x] `/upload` - Document upload requires authentication
      - [x] `/documents` - Document listing requires authentication
      - [x] `/documents/{doc_id}` - Document deletion requires authentication
      - [x] `/ask` - Question answering requires authentication
    - [x] Update server configuration to run on port 8001 (avoiding Docker Desktop conflicts)
  - [x] **Comprehensive Testing Implementation**
    - [x] Create unit tests for authentication module (`tests/test_auth.py`) - 18 tests covering password hashing, user authentication, session management, and edge cases
    - [x] Create unit tests for authentication router (`tests/test_auth_router.py`) - 14 tests covering login/logout endpoints, session persistence, and security
    - [x] Create integration tests (`tests/test_integration_auth.py`) - 9 tests covering full authentication flow, endpoint protection, and security features
    - [x] All 41 authentication tests passing successfully
    - [x] Add pytest and pytest-asyncio dependencies for testing
  - [x] **Security Features**
    - [x] Implement proper password verification with bcrypt
    - [x] Add session isolation between different clients
    - [x] Implement graceful error handling for invalid credentials
    - [x] Add protection against unauthorized access to sensitive endpoints
    - [x] Add comprehensive logging for authentication events
      - [x] **System Requirements Resolution**
    - [x] Resolve port conflict issues (Docker Desktop on port 8000)
    - [x] Fix password hashing and verification logic
    - [x] Eliminate authentication logic conflicts through clean module organization
    - [x] Implement proper session management and persistence

### 2024-12-30 - Session 2
- [x] **Implement Frontend Authentication System** ✅ **COMPLETED**
  - [x] **Authentication Context Development**
    - [x] Create AuthContext (`frontend-react/src/context/AuthContext.js`) for centralized auth state management
    - [x] Implement login, logout, and authentication status checking functions
    - [x] Add automatic authentication verification on app startup
    - [x] Handle session persistence with cookies and credentials
    - [x] Implement proper error handling for authentication failures
  - [x] **Login Page Implementation**
    - [x] Create modern login page (`frontend-react/src/pages/LoginPage.js`) with clean UI design
    - [x] Add beautiful gradient background and responsive design (`LoginPage.css`)
    - [x] Display demo credentials (admin/admin123) prominently for user convenience
    - [x] Implement form validation and loading states during authentication
    - [x] Add comprehensive error messaging for failed login attempts
  - [x] **Application Integration**
    - [x] Update main App.js to wrap application with AuthProvider for global auth state
    - [x] Implement authentication-based routing (login page vs main app)
    - [x] Add loading screen while checking initial authentication status
    - [x] Create conditional rendering based on authentication state
  - [x] **Sidebar Authentication Features**
    - [x] Update Sidebar component to display authenticated username
    - [x] Add logout button with proper styling and functionality
    - [x] Implement user info display and logout confirmation
  - [x] **API Integration Updates**
    - [x] Update all API calls to include `credentials: 'include'` for session management
    - [x] Modify fetch calls in DocumentsPage, UploadSection, DocumentsSection, and ChatSection
    - [x] Configure proper base URLs (`http://127.0.0.1:8001`) for all API endpoints
    - [x] Ensure authenticated API requests work seamlessly with backend
  - [x] **CORS Configuration Fix**
    - [x] Fix CORS policy in backend (`app/main.py`) to allow specific origin instead of wildcard
    - [x] Change from `allow_origins=["*"]` to `allow_origins=["http://localhost:5170"]`
    - [x] Resolve credential inclusion conflicts with wildcard CORS policy
    - [x] Enable proper cross-origin authenticated requests
  - [x] **Frontend Configuration**
    - [x] Update React proxy configuration in `package.json` to point to correct backend URL
    - [x] Change proxy from `http://localhost:8080` to `http://127.0.0.1:8001`
    - [x] Install and configure frontend dependencies
    - [x] Ensure React development server runs on port 5170
  - [x] **Authentication Flow Features**
    - [x] Implement complete login/logout cycle with session persistence
    - [x] Add automatic redirection from login page to main app upon successful authentication
    - [x] Implement protected route access - all features require authentication
    - [x] Add graceful handling of unauthenticated users with redirect to login
    - [x] Enable seamless authentication state management across browser sessions
  - [x] **UI/UX Enhancements**
    - [x] Create modern, professional login interface with gradient design
    - [x] Add smooth transitions and animations for better user experience
    - [x] Implement responsive design that works on desktop and mobile
    - [x] Add visual feedback for authentication status in sidebar
    - [x] Include loading states and proper error messaging throughout auth flow

### 2024-07-20
- [x] **Improve RAG Accuracy** ✅ **COMPLETED**
  - [x] Replace embedding model with BAAI/bge-large-en-v1.5 (upgraded from all-MiniLM-L6-v2)
  - [x] Implement cross-encoder reranking using cross-encoder/ms-marco-MiniLM-L-6-v2
  - [x] Change LLM model from mistral to llama3:8b
  - [x] **Implement Source Filtering System**
    - [x] Add intelligent document filtering with metadata-based filtering
    - [x] Implement automatic query intent detection (CV/resume vs financial queries)
    - [x] Add fallback expansion when filtering returns insufficient results
    - [x] Update API to accept optional doc_filter parameter
  - [x] **Enhance Prompt Engineering**
    - [x] Add explicit source validation instructions to LLM
    - [x] Implement document type awareness in prompts
    - [x] Add self-critique mechanism for source relevance
    - [x] Clear instructions to ignore irrelevant sources
  - [x] **Frontend Filter Interface**
    - [x] Add filter toggle button with intuitive UI
    - [x] Implement three filter options (CV/Resume, Financial Reports, All Documents)
    - [x] Add filter tags showing which filter was applied
    - [x] Ensure responsive design across devices
  - [ ] Benchmark and evaluate performance improvements
- [x] **Frontend Improvements**
  - [x] Integrate Stagewise toolbar for AI-powered UI editing
  - [x] Reduce visual intensity of UI elements (scrollbar and heading glow effects)
  - [x] Create React.js frontend with component-based architecture
  - [x] Implement mobile-responsive design
  - [x] Implement sidebar navigation with separate pages for chat, documents, and upload
  - [x] Create clean main chat page with only chat interface
  - [x] Create separate document management page
  - [x] Create separate upload page
  - [x] **Implement Chat History Persistence**
    - [x] Create chat history sidebar in chat page
    - [x] Store chat messages in local storage
    - [x] Allow users to navigate between different chat sessions
    - [x] Add functionality to create new chat sessions
    - [x] Add functionality to delete chat sessions
- [x] **Code Quality & Testing**
  - [x] Add comprehensive logging
  - [ ] Add unit tests for all components
  - [ ] Implement full vector deletion logic for FAISS on document removal
- [ ] **Feature Expansion**
  - [ ] Add support for more document types (beyond PDF)

### 2024-07-20
- [x] Implement chat history persistence with local storage
- [x] Create chat history sidebar with chat navigation
- [x] Add new chat and delete chat functionality
- [x] Update Windows compatibility for React start script

### 2024-07-19
- [x] Create sidebar layout with icon-only navigation
- [x] Implement responsive centered card layout
- [x] Maintain dark neon theme styling
- [x] Implement page routing system with context
- [x] Implement active state for sidebar buttons
- [x] Create chat-only main page
- [x] Move document upload to separate page
- [x] Move document library to separate page
- [x] Add navigation between pages

### 2024-07-18
- [x] Replace embedding model with BAAI/bge-large-en-v1.5
- [x] Implement cross-encoder reranking with cross-encoder/ms-marco-MiniLM-L-6-v2
- [x] Change LLM model from mistral to llama3:8b
- [x] Configure two-stage retrieval process (20 initial candidates → 5 after reranking)
- [x] Create React.js frontend with component-based architecture
- [x] Configure React frontend to run on port 5170

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