# Hybrid RAG Chatbot

A hybrid RAG (Retrieval Augmented Generation) chatbot system for answering questions based on PDF documents. The system uses FAISS for vector storage, Sentence Transformers for embeddings, and Ollama for generating responses (with fallback mechanisms when Ollama is unavailable).

## Features

- PDF document processing and chunking
- FAISS vector database for semantic search
- Integration with Ollama for LLM-powered responses
- Fallback mechanisms when Ollama is unavailable
- FastAPI backend with HTML/JS frontend
- Document management (upload, list)
- Question answering based on uploaded documents

## Requirements

- Python 3.9+
- Sentence Transformers
- FAISS
- PyPDF
- FastAPI
- Ollama (optional, for better responses)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hybrid-rag-chatbot.git
cd hybrid-rag-chatbot
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. (Optional) Install and start Ollama:
   - Follow instructions at [Ollama's website](https://ollama.ai/) to install
   - Pull the required model: `ollama pull mistral`
   - Start the Ollama server

## Usage

1. Start the server:
```bash
python -m uvicorn app.main:app --reload
```

2. Open your browser and navigate to `http://localhost:8000`

3. Upload PDF documents through the web interface

4. Ask questions about the uploaded documents

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

## Architecture Notes

The application employs a standard RAG architecture:

1.  **Frontend:** An HTML/JavaScript interface (served by FastAPI) allows users to upload PDFs and ask questions.
2.  **Backend (FastAPI):** Handles API requests for document upload, listing, deletion, and question answering.
3.  **Document Processing (`app/utils/file_loader.py`):** Extracts text from PDFs, splits it into chunks, and generates embeddings using Sentence Transformers (`all-MiniLM-L6-v2`).
4.  **Vector Store (FAISS):** Stores the document chunk embeddings for efficient similarity search. The FAISS index (`index.faiss` and `index.pkl`) is saved locally in `data/vector_store/`.
5.  **Retriever (`app/retrievers/rag.py`):** Takes a user's question, embeds it, and queries the FAISS vector store to find the most relevant document chunks (`k=5` by default).
6.  **LLM Integration (`app/llm/ollama_runner.py`):** Sends the user's question along with the retrieved context chunks to an Ollama instance (running a model like Mistral) to generate a final answer. If Ollama is unavailable, it falls back to returning the raw retrieved context.
7.  **Document Index (`data/document_index.json`):** A simple JSON file maintains a mapping between uploaded document metadata (title, filename) and a unique ID, used for listing and deleting documents.

### Vector Store Deletion Handling

A key challenge addressed during development was ensuring that deleting a document properly removed its context from the system.

*   **Initial Problem:** The initial implementation of the document deletion endpoint (`DELETE /documents/{doc_id}`) successfully removed the document's entry from `document_index.json` and deleted the source PDF file. However, it did *not* remove the corresponding vector embeddings from the FAISS index file (`data/vector_store/index.faiss`). This meant that even after a document was "deleted", its content could still be retrieved and used in answers, leading to incorrect or irrelevant responses.

*   **Fix Implemented:** The `DELETE /documents/{doc_id}` endpoint in `app/main.py` was modified to implement a "nuke and rebuild" strategy for the vector store upon deletion:
    1.  The document entry is removed from `document_index.json`.
    2.  The original PDF file is deleted from `data/documents/`.
    3.  The system identifies all *remaining* documents based on the updated `document_index.json`.
    4.  It re-processes all chunks for these remaining documents.
    5.  A completely *new* FAISS index is built from scratch using only the chunks from the remaining documents. This new index overwrites the old `index.faiss` and `index.pkl` files.
    6.  If no documents remain after deletion, the `index.faiss` and `index.pkl` files are explicitly deleted.
    7.  The in-memory cache of the vector store (`rag_retriever.vectorstore`) is cleared to force a reload from the updated disk state on the next query.

*   **Outcome:** This ensures the FAISS vector store always accurately reflects the currently indexed documents. Context from deleted documents is reliably removed, preventing outdated information from influencing search results and LLM responses.

## Testing

Run the test script to verify the application functionality:
```