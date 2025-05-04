# Chatbot RAG Architecture Diagrams

This document provides diagrams illustrating the key workflows of the Hybrid RAG Chatbot application.

## Document Upload Flow

This diagram shows the sequence of events when a user uploads a PDF document.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend (FastAPI)
    participant FileLoader
    participant RAGRetriever
    participant FAISS_Store
    participant DocIndexJSON

    User->>Frontend: Selects PDF, provides Title, Clicks Upload
    Frontend->>Backend: POST /upload (file, title)
    Backend->>FileLoader: prepare_documents(pdf_path, title, doc_id)
    FileLoader->>FileLoader: Extract Text & Chunk
    FileLoader->>FileLoader: Generate Embeddings (SentenceTransformer)
    FileLoader-->>Backend: Return chunks (List[Document])
    Backend->>RAGRetriever: load_vectorstore()
    RAGRetriever->>FAISS_Store: Load index.faiss/pkl (if exists)
    FAISS_Store-->>RAGRetriever: Vector store instance (or None)
    RAGRetriever-->>Backend: Existing store loaded (or not)
    alt Existing Store Found
        Backend->>RAGRetriever: vectorstore.add_documents(chunks)
        RAGRetriever->>FAISS_Store: Add new vectors
    else No Existing Store / First Upload
        Backend->>RAGRetriever: build_vectorstore(chunks)
        RAGRetriever->>FAISS_Store: Create new index from chunks
    end
    Backend->>RAGRetriever: save_vectorstore()
    RAGRetriever->>FAISS_Store: Save index.faiss/pkl
    FAISS_Store-->>RAGRetriever: Save confirmation
    RAGRetriever-->>Backend: Save confirmation
    Backend->>DocIndexJSON: Load existing index
    DocIndexJSON-->>Backend: Index data
    Backend->>Backend: Add new document entry (doc_id, title, filename)
    Backend->>DocIndexJSON: Save updated index
    DocIndexJSON-->>Backend: Save confirmation
    Backend-->>Frontend: Success Response (doc_id, title)
    Frontend-->>User: Display success message
```

## Question Answering Flow

This diagram shows the sequence for answering a user's question.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend (FastAPI)
    participant RAGRetriever
    participant FAISS_Store
    participant OllamaRunner
    participant LLM (Ollama)

    User->>Frontend: Enters question, Clicks Ask
    Frontend->>Backend: POST /ask (question)
    Backend->>RAGRetriever: load_vectorstore()
    RAGRetriever->>FAISS_Store: Load index.faiss/pkl (if needed)
    FAISS_Store-->>RAGRetriever: Vector store instance
    RAGRetriever-->>Backend: Store loaded
    Backend->>RAGRetriever: retrieve_context(question)
    RAGRetriever->>RAGRetriever: Embed question
    RAGRetriever->>FAISS_Store: Similarity search with question embedding
    FAISS_Store-->>RAGRetriever: Relevant chunk embeddings + metadata
    RAGRetriever->>RAGRetriever: Reconstruct Document objects
    RAGRetriever-->>Backend: List[Document] (relevant chunks)
    Backend->>Backend: Format context string from documents
    Backend->>OllamaRunner: get_answer_from_context(question, context)
    OllamaRunner->>OllamaRunner: Create prompt template
    OllamaRunner->>LLM (Ollama): Send formatted prompt (question + context)
    LLM (Ollama)-->>OllamaRunner: Generated answer string
    OllamaRunner-->>Backend: Answer string
    Backend->>Backend: Format response (answer, sources)
    Backend-->>Frontend: JSON Response (question, answer, sources)
    Frontend-->>User: Display Answer and Sources
```

## Document Deletion Flow

This diagram illustrates the "nuke and rebuild" process when a document is deleted.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend (FastAPI)
    participant DocIndexJSON
    participant FileSystem
    participant RAGRetriever
    participant FileLoader
    participant FAISS_Store

    User->>Frontend: Clicks Delete for a document
    Frontend->>Backend: DELETE /documents/{doc_id}
    Backend->>DocIndexJSON: Load index
    DocIndexJSON-->>Backend: Index data
    Backend->>Backend: Find entry for doc_id, get filename
    Backend->>Backend: Remove entry for doc_id
    Backend->>DocIndexJSON: Save updated index
    DocIndexJSON-->>Backend: Save confirmation
    Backend->>FileSystem: Delete original PDF file (data/documents/{doc_id}_{filename})
    FileSystem-->>Backend: Deletion confirmation
    Backend->>Backend: Get list of *remaining* document info from updated index
    alt Documents Remain
        Backend->>Backend: Iterate remaining docs
        loop For Each Remaining Document
            Backend->>FileSystem: Construct path (data/documents/{id}_{filename})
            FileSystem-->>Backend: Check if path exists
            Backend->>FileLoader: prepare_documents(path, title, id)
            FileLoader-->>Backend: Chunks for one document
            Backend->>Backend: Collect all chunks
        end
        Backend->>RAGRetriever: build_vectorstore(all_remaining_chunks)
        RAGRetriever->>FAISS_Store: Create *new* index from collected chunks (Overwrites old)
        FAISS_Store-->>RAGRetriever: Build confirmation
        RAGRetriever-->>Backend: Build confirmation
    else No Documents Remain
        Backend->>FileSystem: Delete index.faiss (data/vector_store/)
        FileSystem-->>Backend: Deletion confirmation
        Backend->>FileSystem: Delete index.pkl (data/vector_store/)
        FileSystem-->>Backend: Deletion confirmation
    end
    Backend->>RAGRetriever: Clear in-memory store (vectorstore = None)
    RAGRetriever-->>Backend: Cache cleared
    Backend-->>Frontend: Success Response
    Frontend-->>User: Update document list / Show confirmation
``` 