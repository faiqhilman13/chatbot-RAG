<<<<<<< HEAD
# TNB AI Agent Platform

A React-based application featuring various AI agents for data processing, report generation, document review, and classification.

## Features

- SQL Agent: Convert natural language to SQL queries
- Report Generation: Create Excel and PowerPoint reports from documents
- Document Review: Compare documents against reference materials
- Classification Agent: Classify documents based on custom rulesets
- Additional bots for summarization, visualization, and data extraction

## Installation

1. Clone the repository
   ```
   git clone https://github.com/MrGuts13/reactBNT.git
   ```

2. Install dependencies
   ```
   npm install
   ```

3. Start the development server
   ```
   npm run dev
   ```

## Technologies Used

- React
- React Router
- TailwindCSS
- Framer Motion

## License

For internal use only. 
=======
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

## Testing

Run the test script to verify the application functionality:
```bash
python test_rag.py
```

This will:
1. Create a test PDF document
2. Upload it to the system
3. Ask several test questions
4. Clean up afterwards

## Configuration

Configuration options can be modified in `app/config.py`:
- `LLM_MODEL_NAME`: The Ollama model to use (default: "mistral")
- `OLLAMA_BASE_URL`: URL of the Ollama API (default: "http://localhost:11434")
- `RETRIEVAL_K`: Number of documents to retrieve (default: 5)
- `CHUNK_SIZE`: Size of document chunks (default: 500)
- `CHUNK_OVERLAP`: Overlap between document chunks (default: 50)

## Notes

- The system will work with or without Ollama
- When Ollama is not available, the system returns raw context from retrieved documents
- The embedding model used is "all-MiniLM-L6-v2" from Sentence Transformers 
>>>>>>> 4ba6460b90d81cde8ba09b711297f0ecc7855a66
