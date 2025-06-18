# Hybrid RAG Chatbot

A sophisticated Retrieval-Augmented Generation (RAG) chatbot built with FastAPI and React that provides intelligent document-based question answering with advanced source filtering capabilities.

## 🚀 Key Features

### 🎯 **Advanced Source Filtering**
- **Intelligent Document Filtering**: Automatically detects query intent and applies appropriate document filters
- **Manual Filter Controls**: Users can manually select document types (CV/Resume, Financial Reports, All Documents)
- **Automatic Intent Detection**: System recognizes personal vs. financial queries and filters accordingly
- **Fallback Expansion**: Automatically expands search when filtering returns insufficient results

### 🧠 **Enhanced RAG Pipeline**
- **Two-Stage Retrieval**: Uses BAAI/bge-large-en-v1.5 embeddings with cross-encoder reranking
- **Advanced Prompt Engineering**: LLM validates source relevance before generating responses
- **Quality over Quantity**: Prioritizes relevant sources over raw document count
- **Source Validation**: Explicitly ignores irrelevant documents (e.g., financial docs for personal questions)

### 🎨 **Modern React Frontend**
- **Component-Based Architecture**: Clean, maintainable React.js implementation
- **Chat History Persistence**: Local storage-based chat session management
- **Responsive Design**: Works seamlessly across desktop and mobile devices
- **Filter Interface**: Intuitive toggle-based filtering with visual indicators

### 🔧 **Technical Stack**
- **Backend**: FastAPI with Python 3.8+
- **Frontend**: React.js with modern hooks and context
- **Embeddings**: BAAI/bge-large-en-v1.5 (upgraded from all-MiniLM-L6-v2)
- **Reranking**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **LLM**: Ollama with llama3:8b model
- **Vector Store**: FAISS with efficient similarity search
- **Document Processing**: PyPDF with intelligent chunking

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Ollama installed and running (for LLM functionality)
- Git

## 🛠️ Installation

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd chatbot-RAG
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and start Ollama:**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3:8b
   ```

5. **Start the backend server:**
   ```bash
   cd chatbot-RAG
   python -m uvicorn app.main:app --reload --port 8080
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend-react
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

The application will be available at:
- Frontend: http://localhost:5170
- Backend API: http://localhost:8080

## 🎯 Usage

### Document Upload
1. Navigate to the **Upload** page using the sidebar
2. Select a PDF document
3. Optionally provide a custom title
4. Click "Upload and Process" to add it to the knowledge base

### Intelligent Querying
1. Go to the **Chat** page
2. Ask questions about your documents
3. The system automatically applies appropriate filters:
   - **Personal queries** (experience, education, skills) → CV/Resume documents
   - **Financial queries** (revenue, earnings, reports) → Financial documents
4. Use the filter toggle for manual control over document selection

### Document Management
1. Visit the **Documents** page to view all uploaded files
2. Delete documents that are no longer needed
3. Refresh the list to see current status

## 🔍 Filter Examples

The system automatically detects query intent:

```
"Tell me about Faiq's experience at EY"
→ Automatically filters to CV/Resume documents

"What was Tesla's revenue in FY24?"
→ Automatically filters to Financial Report documents

"Summarize all documents"
→ Uses all available documents
```

## 🧪 Testing the Improvements

To test the source filtering improvements:

1. Upload both a CV/resume and a financial report
2. Ask: "List me all of Faiq's experience at EY"
3. Verify that only CV/resume sources appear in the response
4. Check that financial document content is ignored

## 🔧 Configuration

Key configuration options in `app/config.py`:

```python
# Model Settings
LLM_MODEL_NAME = "llama3:8b"
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Retrieval Settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVAL_K = 5  # Final results after reranking
RETRIEVAL_CANDIDATES = 20  # Initial candidates before reranking
```

## 📊 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React.js      │    │   FastAPI        │    │   Ollama        │
│   Frontend      │◄──►│   Backend        │◄──►│   LLM Service   │
│                 │    │                  │    │                 │
│ • Chat Interface│    │ • Source Filter  │    │ • llama3:8b     │
│ • Filter Controls│   │ • Intent Detection│   │ • Response Gen  │
│ • Document Mgmt │    │ • RAG Pipeline   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   FAISS Vector   │
                       │   Store          │
                       │                  │
                       │ • BGE Embeddings │
                       │ • Cross-Encoder  │
                       │ • Metadata Index │
                       └──────────────────┘
```

## 🎉 Recent Improvements

### ✅ Source Filtering System
- Intelligent document filtering with automatic intent detection
- Manual filter controls with visual feedback
- Fallback expansion when filtering returns too few results

### ✅ Enhanced Prompt Engineering
- Source validation instructions for LLM
- Document type awareness to ignore irrelevant sources
- Self-critique mechanism for better accuracy

### ✅ Upgraded Models
- BAAI/bge-large-en-v1.5 embeddings (improved from all-MiniLM-L6-v2)
- cross-encoder/ms-marco-MiniLM-L-6-v2 reranking
- llama3:8b LLM (upgraded from mistral)

## 🚀 Future Enhancements

- [ ] Performance benchmarking and evaluation metrics
- [ ] Additional document type support beyond PDF
- [ ] Advanced analytics and usage insights
- [ ] Real-time response streaming
- [ ] Document preview and highlighting
- [ ] Custom user-defined filters and tags

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Ollama Connection Error:**
- Ensure Ollama is installed and running: `ollama serve`
- Check if the model is available: `ollama list`
- Pull the required model: `ollama pull llama3:8b`

**Frontend Not Loading:**
- Verify Node.js version (14+)
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**Empty Responses:**
- Upload documents first before asking questions
- Check that the vector store is properly initialized
- Verify document processing completed successfully

For more issues, check the console logs and ensure all dependencies are properly installed.