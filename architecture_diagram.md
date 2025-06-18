# Architecture Diagrams

This file contains the mermaid diagrams for the Hybrid RAG Chatbot application workflows.

## Document Upload Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant FL as FileLoader
    participant R as RAGRetriever
    participant FS as FAISS_Store
    participant DJ as DocIndexJSON

    U->>F: Selects PDF, provides Title, Clicks Upload
    F->>B: POST /upload (file, title)
    B->>FL: prepare_documents(pdf_path, title, doc_id)
    FL->>FL: Extract Text & Chunk
    FL->>FL: Generate Embeddings (BAAI/bge-large-en-v1.5)
    FL-->>B: Return chunks (List[Document])
    B->>R: load_vectorstore()
    R->>FS: Load index.faiss/pkl (if exists)
    FS-->>R: Vector store instance (or None)
    R-->>B: Existing store loaded (or not)
    alt Existing Store Found
        B->>R: vectorstore.add_documents(chunks)
        R->>FS: Add new vectors
    else No Existing Store / First Upload
        B->>R: build_vectorstore(chunks)
        R->>FS: Create new index from chunks
    end
    B->>R: save_vectorstore()
    R->>FS: Save index.faiss/pkl
    FS-->>R: Save confirmation
    R-->>B: Save confirmation
    B->>DJ: Load existing index
    DJ-->>B: Index data
    B->>B: Add new document entry (doc_id, title, filename)
    B->>DJ: Save updated index
    DJ-->>B: Save confirmation
    B-->>F: Success Response (doc_id, title)
    F-->>U: Display success message
```

## Question Answering Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant R as RAGRetriever
    participant FS as FAISS_Store
    participant CE as CrossEncoder
    participant OR as OllamaRunner
    participant LLM as LLM_Model

    U->>F: Enters question, Clicks Ask
    F->>B: POST /ask (question)
    B->>R: load_vectorstore()
    R->>FS: Load index.faiss/pkl (if needed)
    FS-->>R: Vector store instance
    R-->>B: Store loaded
    B->>R: retrieve_context(question)
    R->>R: Embed question with BAAI/bge-large-en-v1.5
    R->>FS: Similarity search for 20 candidates
    FS-->>R: Candidate chunk embeddings + metadata
    R->>CE: Rerank candidates with question
    CE->>CE: Score (question, chunk) pairs
    CE-->>R: Reranked candidates with scores
    R->>R: Select top 5 chunks after reranking
    R-->>B: List[Document] (most relevant chunks)
    B->>B: Format context string from documents
    B->>OR: get_answer_from_context(question, context)
    OR->>OR: Create prompt template
    OR->>LLM: Send formatted prompt (question + context)
    LLM-->>OR: Generated answer string
    OR-->>B: Answer string
    B->>B: Format response (answer, sources)
    B-->>F: JSON Response (question, answer, sources)
    F-->>U: Display Answer and Sources
```

## Document Deletion Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DJ as DocIndexJSON
    participant FileSys as FileSystem
    participant R as RAGRetriever
    participant FL as FileLoader
    participant FS as FAISS_Store

    U->>F: Clicks Delete for a document
    F->>B: DELETE /documents/{doc_id}
    B->>DJ: Load index
    DJ-->>B: Index data
    B->>B: Find entry for doc_id, get filename
    B->>B: Remove entry for doc_id
    B->>DJ: Save updated index
    DJ-->>B: Save confirmation
    B->>FileSys: Delete original PDF file
    FileSys-->>B: Deletion confirmation
    B->>B: Get list of remaining document info from updated index
    alt Documents Remain
        B->>B: Iterate remaining docs
        loop For Each Remaining Document
            B->>FileSys: Construct path
            FileSys-->>B: Check if path exists
            B->>FL: prepare_documents(path, title, id)
            FL-->>B: Chunks for one document
            B->>B: Collect all chunks
        end
        B->>R: build_vectorstore(all_remaining_chunks)
        R->>FS: Create new index from collected chunks
        FS-->>R: Build confirmation
        R-->>B: Build confirmation
    else No Documents Remain
        B->>FileSys: Delete index.faiss
        FileSys-->>B: Deletion confirmation
        B->>FileSys: Delete index.pkl
        FileSys-->>B: Deletion confirmation
    end
    B->>R: Clear in-memory store
    R-->>B: Cache cleared
    B-->>F: Success Response
    F-->>U: Update document list / Show confirmation
``` 