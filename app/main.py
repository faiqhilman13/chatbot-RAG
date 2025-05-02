from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil
import uuid
from app.routers import ask
from app.config import DOCUMENTS_DIR, VECTORSTORE_DIR
from app.retrievers.rag import rag_retriever
from app.utils.file_loader import prepare_documents

# Create FastAPI app
app = FastAPI(title="Hybrid RAG Chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ask.router)

# Sample HTML for the UI
def get_html_content():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hybrid RAG Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; }
            h1 { color: #3a3a3a; border-bottom: 2px solid #5e9ca0; padding-bottom: 10px; }
            .section { margin-bottom: 30px; border: 1px solid #ddd; padding: 20px; border-radius: 8px; background-color: #f9f9f9; }
            .section h2 { color: #5e9ca0; margin-top: 0; }
            button, input[type="submit"] { background-color: #5e9ca0; color: white; padding: 10px 15px; 
                   border: none; border-radius: 4px; cursor: pointer; margin-top: 10px; }
            button:hover, input[type="submit"]:hover { background-color: #4a8288; }
            input, textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            textarea { min-height: 100px; resize: vertical; }
            pre { background-color: white; padding: 15px; border-radius: 5px; white-space: pre-wrap; border: 1px solid #ddd; overflow-x: auto; }
            .document-card { padding: 10px; margin: 10px 0; background-color: white; border-radius: 5px; border: 1px solid #ddd; }
            .document-title { font-weight: bold; }
            .document-info { font-size: 0.9em; color: #666; }
            .loading { display: inline-block; margin-left: 10px; font-style: italic; color: #666; }
            .chat-container { max-height: 400px; overflow-y: auto; padding: 10px; background-color: white; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px; }
            .chat-question { background-color: #e6f2f2; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
            .chat-answer { background-color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; border-left: 3px solid #5e9ca0; }
            .sources { font-size: 0.8em; font-style: italic; margin-top: 10px; color: #666; }
            .delete-btn { background-color: #e74c3c; color: white; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer; margin-top: 5px; }
            .delete-btn:hover { background-color: #c0392b; }
        </style>
    </head>
    <body>
        <h1>Hybrid RAG Chatbot</h1>
        
        <div class="section">
            <h2>Upload PDF Document</h2>
            <p>Upload PDF documents to build the knowledge base for the chatbot.</p>
            <form id="uploadForm">
                <input type="file" id="fileUpload" accept=".pdf" required>
                <input type="text" id="docTitle" placeholder="Document Title" required>
                <input type="submit" value="Upload and Process">
            </form>
            <div id="uploadStatus"></div>
            <pre id="uploadResult"></pre>
        </div>
        
        <div class="section">
            <h2>Document Library</h2>
            <button onclick="loadDocuments()">Refresh Documents</button>
            <div id="documentList"></div>
        </div>
        
        <div class="section">
            <h2>Test Upload (Debug)</h2>
            <p>This is a simplified upload form for debugging purposes.</p>
            <form id="testUploadForm">
                <input type="file" id="testFileUpload" accept=".pdf">
                <input type="submit" value="Test Upload">
            </form>
            <div id="testUploadStatus"></div>
            <pre id="testUploadResult"></pre>
        </div>
        
        <div class="section">
            <h2>Chat</h2>
            <div class="chat-container" id="chatContainer"></div>
            <textarea id="question" placeholder="Ask a question about the uploaded documents..."></textarea>
            <button onclick="askQuestion()" id="askButton">Ask Question</button>
        </div>
        
        <script>
            // Document upload handling
            document.getElementById('uploadForm').onsubmit = async (e) => {
                e.preventDefault();
                
                const fileInput = document.getElementById('fileUpload');
                const titleInput = document.getElementById('docTitle');
                
                if (!fileInput.files[0] || !titleInput.value.trim()) {
                    alert('Please provide both a file and a title');
                    return;
                }
                
                const file = fileInput.files[0];
                const title = titleInput.value.trim();
                
                // Validate file type
                if (!file.name.toLowerCase().endsWith('.pdf')) {
                    alert('Only PDF files are supported');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('title', title);
                
                const uploadStatus = document.getElementById('uploadStatus');
                uploadStatus.innerHTML = '<div class="loading">Uploading and processing document...</div>';
                
                try {
                    console.log('Sending upload request for file:', file.name, 'with title:', title);
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'Upload failed');
                    }
                    
                    const result = await response.json();
                    console.log('Upload response:', result);
                    
                    uploadStatus.innerHTML = '';
                    document.getElementById('uploadResult').textContent = JSON.stringify(result, null, 2);
                    
                    // Clear form fields
                    fileInput.value = '';
                    titleInput.value = '';
                    
                    // Refresh document list
                    loadDocuments();
                } catch (error) {
                    console.error('Upload error:', error);
                    uploadStatus.innerHTML = '';
                    document.getElementById('uploadResult').textContent = 'Error: ' + error.message;
                }
            };
            
            // Load documents
            async function loadDocuments() {
                const documentList = document.getElementById('documentList');
                documentList.innerHTML = '<div class="loading">Loading documents...</div>';
                
                try {
                    const response = await fetch('/documents');
                    const result = await response.json();
                    
                    if (result.documents && result.documents.length > 0) {
                        documentList.innerHTML = '';
                        result.documents.forEach(doc => {
                            documentList.innerHTML += `
                                <div class="document-card">
                                    <div class="document-title">${doc.title}</div>
                                    <div class="document-info">Filename: ${doc.filename}</div>
                                    <div class="document-info">Pages: ${doc.page_count || 'Unknown'}</div>
                                    <div class="document-info">Size: ${doc.size || 'Unknown'}</div>
                                    <div style="margin-top: 10px; text-align: right;">
                                        <button onclick="deleteDocument('${doc.id}')" style="background-color: #e74c3c; color: white; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer;">Delete Document</button>
                                    </div>
                                </div>
                            `;
                        });
                    } else {
                        documentList.innerHTML = '<p>No documents uploaded yet.</p>';
                    }
                } catch (error) {
                    documentList.innerHTML = '<p>Error loading documents: ' + error.message + '</p>';
                }
            }
            
            // Ask question
            async function askQuestion() {
                const question = document.getElementById('question').value.trim();
                if (!question) return;
                
                const askButton = document.getElementById('askButton');
                const originalText = askButton.textContent;
                askButton.textContent = 'Thinking...';
                askButton.disabled = true;
                
                // Add question to chat UI
                const chatContainer = document.getElementById('chatContainer');
                const questionElement = document.createElement('div');
                questionElement.className = 'chat-question';
                questionElement.textContent = question;
                chatContainer.appendChild(questionElement);
                
                // Create placeholder for answer
                const answerElement = document.createElement('div');
                answerElement.className = 'chat-answer';
                answerElement.textContent = 'Thinking...';
                chatContainer.appendChild(answerElement);
                
                // Scroll to bottom of chat
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                try {
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question })
                    });
                    
                    const result = await response.json();
                    
                    // Update answer in chat UI
                    answerElement.textContent = result.answer;
                    
                    // Add sources if available
                    if (result.sources && result.sources.length > 0) {
                        const sourcesElement = document.createElement('div');
                        sourcesElement.className = 'sources';
                        sourcesElement.textContent = 'Sources: ' + result.sources.join(', ');
                        answerElement.appendChild(sourcesElement);
                    }
                    
                    // Clear question input
                    document.getElementById('question').value = '';
                } catch (error) {
                    answerElement.textContent = 'Error: ' + error.message;
                } finally {
                    askButton.textContent = originalText;
                    askButton.disabled = false;
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }
            
            // Handle Enter key in question input
            document.getElementById('question').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    askQuestion();
                }
            });
            
            // Load documents on page load
            loadDocuments();
            
            // Test Upload handling
            document.getElementById('testUploadForm').onsubmit = async (e) => {
                e.preventDefault();
                
                const fileInput = document.getElementById('testFileUpload');
                
                if (!fileInput.files[0]) {
                    alert('Please select a file for testing');
                    return;
                }
                
                const file = fileInput.files[0];
                
                const formData = new FormData();
                formData.append('file', file);
                
                const uploadStatus = document.getElementById('testUploadStatus');
                uploadStatus.innerHTML = '<div class="loading">Testing upload...</div>';
                
                try {
                    console.log('Sending test upload for file:', file.name);
                    const response = await fetch('/test-upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'Test upload failed');
                    }
                    
                    const result = await response.json();
                    console.log('Test upload response:', result);
                    
                    uploadStatus.innerHTML = '';
                    document.getElementById('testUploadResult').textContent = JSON.stringify(result, null, 2);
                    
                    // Clear form field
                    fileInput.value = '';
                    
                    // Refresh document list
                    loadDocuments();
                } catch (error) {
                    console.error('Test upload error:', error);
                    uploadStatus.innerHTML = '';
                    document.getElementById('testUploadResult').textContent = 'Error: ' + error.message;
                }
            };
            
            // Delete document
            async function deleteDocument(docId) {
                if (!confirm('Are you sure you want to delete this document?')) {
                    return;
                }
                
                try {
                    console.log('Deleting document:', docId);
                    const response = await fetch(`/documents/${docId}`, {
                        method: 'DELETE'
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'Delete failed');
                    }
                    
                    const result = await response.json();
                    console.log('Delete response:', result);
                    
                    // Refresh document list
                    loadDocuments();
                } catch (error) {
                    console.error('Delete error:', error);
                    alert('Error deleting document: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def root():
    """Return the HTML UI"""
    return HTMLResponse(content=get_html_content())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    vectorstore_exists = os.path.exists(os.path.join(VECTORSTORE_DIR, "index.faiss"))
    
    return {
        "status": "healthy",
        "documents_dir_exists": os.path.exists(DOCUMENTS_DIR),
        "vectorstore_exists": vectorstore_exists,
        "document_count": len(os.listdir(DOCUMENTS_DIR)) if os.path.exists(DOCUMENTS_DIR) else 0
    }

# Document storage
document_store = {}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), title: str = Form(...)):
    """Upload and process a PDF document"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Create a unique ID for the document
    doc_id = str(uuid.uuid4())
    
    # Make sure directories exist
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    
    # Debug information
    print(f"Uploading document: {file.filename}")
    print(f"Document ID: {doc_id}")
    print(f"Document Title: {title}")
    print(f"DOCUMENTS_DIR: {DOCUMENTS_DIR}")
    print(f"DOCUMENTS_DIR exists: {os.path.exists(DOCUMENTS_DIR)}")
    
    # Save the file
    file_location = os.path.join(DOCUMENTS_DIR, f"{doc_id}_{file.filename}")
    print(f"Saving file to: {file_location}")
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"File saved successfully to {file_location}")
        print(f"File exists after save: {os.path.exists(file_location)}")
    except Exception as e:
        error_message = f"Error saving file: {str(e)}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)
    
    # Process the document
    try:
        # Process the document and add to vectorstore
        print(f"Processing document: {file_location}")
        docs = prepare_documents(file_location)
        print(f"Document processed: {len(docs) if docs else 0} chunks created")
        
        # Store document metadata
        file_size = os.path.getsize(file_location)
        file_size_kb = round(file_size / 1024, 2)
        
        document_store[doc_id] = {
            "id": doc_id,
            "title": title,
            "filename": file.filename,
            "path": file_location,
            "size": f"{file_size_kb} KB",
            "chunk_count": len(docs) if docs else 0
        }
        print(f"Document metadata stored: {document_store[doc_id]}")
        
        # Add to vectorstore
        if docs:
            # Ensure vectorstore is loaded
            print("Loading vectorstore")
            vectorstore_loaded = rag_retriever.load_vectorstore()
            print(f"Vectorstore loaded: {vectorstore_loaded}")
            
            if not vectorstore_loaded:
                print("Building new vectorstore")
                rag_retriever.build_vectorstore(docs)
            else:
                # Add to existing vectorstore
                print("Adding documents to existing vectorstore")
                rag_retriever.vectorstore.add_documents(docs)
                print("Saving vectorstore")
                rag_retriever.save_vectorstore()
        
        return {
            "id": doc_id,
            "title": title,
            "filename": file.filename,
            "status": "success",
            "message": f"Document uploaded and processed successfully. Created {len(docs) if docs else 0} chunks."
        }
    except Exception as e:
        error_message = f"Error processing document: {str(e)}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)

@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    return {"documents": list(document_store.values())}

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Test endpoint for file upload"""
    # Make sure directories exist
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    
    # Debug information
    print(f"TEST UPLOAD - File: {file.filename}")
    print(f"TEST UPLOAD - DOCUMENTS_DIR: {DOCUMENTS_DIR}")
    print(f"TEST UPLOAD - DOCUMENTS_DIR exists: {os.path.exists(DOCUMENTS_DIR)}")
    
    # Save the file with a fixed name for testing
    file_location = os.path.join(DOCUMENTS_DIR, f"test_{file.filename}")
    print(f"TEST UPLOAD - Saving file to: {file_location}")
    
    try:
        # Try to create an empty test file first
        test_file = os.path.join(DOCUMENTS_DIR, "write_test.txt")
        with open(test_file, "w") as f:
            f.write("Test write")
        print(f"TEST UPLOAD - Test file created: {os.path.exists(test_file)}")
        
        # Now try to save the uploaded file
        with open(file_location, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"TEST UPLOAD - File saved: {os.path.exists(file_location)}")
        
        # Return a simple response
        return {
            "filename": file.filename,
            "saved_to": file_location,
            "exists": os.path.exists(file_location),
            "size": os.path.getsize(file_location) if os.path.exists(file_location) else 0
        }
    except Exception as e:
        error_message = f"TEST UPLOAD - Error: {str(e)}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the system"""
    if doc_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get document path
    doc_path = document_store[doc_id]["path"]
    
    # Check if file exists
    if not os.path.exists(doc_path):
        # Document metadata exists but file is missing
        del document_store[doc_id]
        return {"status": "success", "message": "Document metadata removed (file was missing)"}
    
    # Try to delete the file
    try:
        os.remove(doc_path)
        print(f"Deleted document file: {doc_path}")
        
        # Remove from document store
        del document_store[doc_id]
        
        return {
            "status": "success", 
            "message": "Document deleted successfully"
        }
    except Exception as e:
        error_message = f"Error deleting document: {str(e)}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)

if __name__ == "__main__":
    # Create directories if they don't exist
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    
    # Run the server
    print("Starting Hybrid RAG Chatbot server on http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 