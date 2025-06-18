from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
import shutil
import uuid
from pathlib import Path
import sys # Add import for sys
import json # Add import for json
from app.routers import ask, auth
from app.config import DOCUMENTS_DIR, VECTORSTORE_DIR, BASE_DIR, SESSION_SECRET_KEY, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from app.retrievers.rag import rag_retriever
from app.utils.file_loader import prepare_documents
from app.auth import require_auth, optional_auth
import traceback # Add import for traceback module

# CURSOR: This file should only handle route wiring, not business logic.
# All logic must be called from services/ or utils/

# Create FastAPI app
app = FastAPI(title="Hybrid RAG Chatbot")

# Add session middleware (must be added before other middleware that uses sessions)
app.add_middleware(
    SessionMiddleware, 
    secret_key=SESSION_SECRET_KEY,
    max_age=3600,  # 1 hour session timeout
    same_site="lax",  # Allow cross-site requests for development
    https_only=False  # Allow HTTP for development (set to True in production)
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5170"], # Specific frontend origin for credentials
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],  # Restrict methods
    allow_headers=["Content-Type", "Authorization"],  # Restrict headers
)

# Include API routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(ask.router, prefix="/api")

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# --- Define frontend path ---
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

# --- Mount static files directory ---
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    print(f"Warning: Static directory not found at {STATIC_DIR}")

# --- Remove old HTML content function ---
# def get_html_content():
#    ... (removed large HTML block)

# --- Root endpoint to serve index.html ---
@app.get("/", include_in_schema=False) # exclude from OpenAPI docs
async def read_index():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.is_file():
        print(f"Error: index.html not found at {index_path}")
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(index_path)

# --- Health Check Endpoint ---
@app.get("/health", tags=["System"])
async def health_check():
    # Check basic functionality, e.g., vector store accessibility
    vector_store_exists = VECTORSTORE_DIR.exists() and any(VECTORSTORE_DIR.iterdir())
    # ollama_available = check_ollama_status() # Assuming a check function exists
    return JSONResponse({
        "status": "ok",
        "vector_store_initialized": vector_store_exists,
        # "ollama_available": ollama_available
    })

# Define path for the document index JSON file
DOCUMENT_INDEX_PATH = BASE_DIR / "data" / "document_index.json"

# Helper function to load/save the JSON index
def load_document_index():
    if not DOCUMENT_INDEX_PATH.exists():
        return {}
    try:
        with open(DOCUMENT_INDEX_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading document index {DOCUMENT_INDEX_PATH}: {e}")
        return {}

def save_document_index(index_data):
    try:
        with open(DOCUMENT_INDEX_PATH, 'w') as f:
            json.dump(index_data, f, indent=4)
    except IOError as e:
        print(f"Error saving document index {DOCUMENT_INDEX_PATH}: {e}")

# --- Document Management Endpoints ---

@app.post("/api/upload", tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...), 
    title: str = Form(None),
    current_user: str = Depends(require_auth)
):
    # CURSOR: Logic should ideally be in a service function
    
    # Security validations
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed")
    
    # Check file size
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Validate filename characters (prevent path traversal)
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.() ")
    if not all(c in safe_chars for c in file.filename):
        raise HTTPException(status_code=400, detail="Invalid characters in filename")

    # Use provided title or filename
    doc_title = title.strip() if title and title.strip() else file.filename
    
    # Generate a unique ID for the document for internal tracking
    # This ID is separate from how vector stores might handle IDs.
    doc_id = str(uuid.uuid4())
    
    # Define safe filename and save path
    # Example: use doc_id to avoid collisions, keep original extension
    safe_filename = f"{doc_id}_{file.filename}" 
    save_path = DOCUMENTS_DIR / safe_filename
    
    upload_status = {
        "filename": file.filename,
        "content_type": file.content_type,
        "title": doc_title,
        "doc_id": doc_id, # Return the generated ID
        "status": "",
        "detail": ""
    }

    try:
        # Save the uploaded file
        print(f"Saving uploaded file to: {save_path}")
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"File saved successfully: {save_path}")

        # Process the document to get chunks
        print(f"Preparing document chunks for: {doc_title}")
        chunks = prepare_documents([str(save_path)], title=doc_title, doc_id=doc_id)
        
        if not chunks:
            print(f"No chunks generated for {doc_title}. Aborting vector store update.")
            # Clean up saved file? Or keep it?
            # Let's keep it for now, but raise an error indicating processing failure.
            raise HTTPException(status_code=500, detail=f"Failed to generate document chunks for {doc_title}.")

        print(f"Generated {len(chunks)} chunks. Building/updating vector store...")
        # --- Modify Vector Store Update Logic ---
        vectorstore_updated = False
        try:
            # Attempt to load the existing store first
            if rag_retriever.load_vectorstore():
                print("Existing vector store loaded. Adding new documents...")
                # Use the 'add_documents' method of the loaded FAISS store
                rag_retriever.vectorstore.add_documents(chunks)
                print(f"Added {len(chunks)} chunks to existing vector store.")
                # Save the updated store
                if rag_retriever.save_vectorstore():
                    vectorstore_updated = True
                else:
                    print("Failed to save updated vector store.")
            else:
                # If no store exists, build a new one
                print("No existing vector store found. Building new one...")
                if rag_retriever.build_vectorstore(chunks): # build_vectorstore already saves
                    vectorstore_updated = True
                else:
                    print("Failed to build new vector store.")

            if not vectorstore_updated:
                 raise HTTPException(status_code=500, detail=f"Failed to update or build vector store for {doc_title}.")
            
            print(f"Vector store updated successfully for: {doc_title}")

        except Exception as vs_error:
             print(f"Error during vector store operation: {vs_error}")
             traceback.print_exc()
             raise HTTPException(status_code=500, detail=f"Failed during vector store operation for {doc_title}: {vs_error}")
        # --- End Modify Vector Store Update Logic ---
        
        # --- Update JSON Index (Keep this) ---
        index_data = load_document_index()
        index_data[doc_id] = {"title": doc_title, "filename": file.filename, "id": doc_id}
        save_document_index(index_data)
        print(f"Updated document index with ID: {doc_id}")
        # --- End Update JSON Index ---
        
        upload_status["status"] = "success"
        upload_status["detail"] = f"Document '{doc_title}' processed and added successfully."
        
        return JSONResponse(content=upload_status, status_code=200)

    except Exception as e:
        print("---------- UPLOAD ERROR ----------")
        print(f"Error processing document '{doc_title}' (ID: {doc_id}): {e}")
        traceback.print_exc() # Print the full traceback to the console
        print("----------------------------------")
        
        # Attempt to clean up the saved file if processing failed
        if save_path.exists():
             try:
                 os.remove(save_path)
                 print(f"Cleaned up failed upload: {save_path}")
             except OSError as rm_error:
                 print(f"Error cleaning up file {save_path}: {rm_error}")
        
        upload_status["status"] = "error"
        upload_status["detail"] = f"Failed to process document: {str(e)}"
        raise HTTPException(status_code=500, detail=upload_status["detail"])
    finally:
        await file.close()

@app.get("/api/documents", tags=["Documents"])
async def list_documents(current_user: str = Depends(require_auth)):
    # --- Read from JSON Index --- 
    print("Loading documents from JSON index...")
    index_data = load_document_index()
    # Convert the dictionary values to a list for the frontend
    documents_list = list(index_data.values())
    print(f"Found {len(documents_list)} documents in index.")
    return JSONResponse({"documents": documents_list})
    # --- End Read from JSON Index ---

@app.delete("/api/documents/{doc_id}", tags=["Documents"])
async def delete_document(doc_id: str, current_user: str = Depends(require_auth)):
    print(f"--- Starting Deletion Process for doc_id: {doc_id} ---")
    index_entry_found = False
    original_filename = None # Store filename for file deletion

    # --- Load Index First ---
    index_data = load_document_index()
    if doc_id in index_data:
        index_entry_found = True
        original_filename = index_data[doc_id].get("filename") # Get filename
        print(f"  [Delete] Found document '{index_data[doc_id].get('title', 'N/A')}' in index.")
        # Remove from index immediately
        del index_data[doc_id]
        save_document_index(index_data)
        print(f"  [Delete] Removed doc_id {doc_id} from document index.")
    else:
        print(f"  [Delete] doc_id {doc_id} not found in document index.")
        raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found in index.")

    # --- Delete the original file ---
    file_deleted = False
    if original_filename:
        safe_filename = f"{doc_id}_{original_filename}"
        file_path_to_delete = DOCUMENTS_DIR / safe_filename
        print(f"  [Delete] Attempting to delete file: {file_path_to_delete}")
        if file_path_to_delete.exists():
            try:
                os.remove(file_path_to_delete)
                print(f"  [Delete] Successfully deleted original file: {file_path_to_delete}")
                file_deleted = True
            except OSError as rm_error:
                print(f"  [Delete] Error deleting original file {file_path_to_delete}: {rm_error}")
        else:
            print(f"  [Delete] Original file not found for deletion: {file_path_to_delete}")
    else:
         print(f"  [Delete] Original filename not found in index for doc_id {doc_id}, cannot delete file.")

    # --- Rebuild Vector Store ---
    rebuild_successful = False
    print("  [Delete] Rebuilding vector store from remaining documents...")
    try:
        remaining_docs_info = list(index_data.values()) # Use the updated index_data
        print(f"  [Delete] Found {len(remaining_docs_info)} remaining documents in index.")

        if remaining_docs_info:
            all_remaining_chunks = []
            print("  [Delete] Processing remaining documents for chunks...")
            for doc_info in remaining_docs_info:
                if "id" in doc_info and "filename" in doc_info:
                    remaining_safe_filename = f"{doc_info['id']}_{doc_info['filename']}"
                    path = str(DOCUMENTS_DIR / remaining_safe_filename)
                    print(f"    [Delete] Checking remaining file: {path}")
                    if os.path.exists(path):
                       print(f"      [Delete] Processing chunks for: {path}")
                       chunks = prepare_documents([path], title=doc_info.get("title"), doc_id=doc_info["id"])
                       if chunks:
                           all_remaining_chunks.extend(chunks)
                           print(f"      [Delete] Added {len(chunks)} chunks.")
                       else:
                           print(f"      [Delete] Warning: No chunks generated for remaining file {path}")
                    else:
                         print(f"    [Delete] Skipping non-existent file for rebuild: {path}")
                else:
                     print(f"    [Delete] Warning: Incomplete info for a remaining document: {doc_info}")

            if all_remaining_chunks:
                print(f"  [Delete] Building new vector store with {len(all_remaining_chunks)} total chunks.")
                # Ensure vectorstore directory exists
                VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
                rebuild_successful = rag_retriever.build_vectorstore(all_remaining_chunks)
                if rebuild_successful:
                    print("  [Delete] Vector store rebuilt successfully.")
                else:
                    print("  [Delete] Failed to rebuild vector store.")
            else:
                 print("  [Delete] No valid remaining documents or chunks generated. Clearing vector store.")
                 try:
                     faiss_path = VECTORSTORE_DIR / "index.faiss"
                     pkl_path = VECTORSTORE_DIR / "index.pkl"
                     print(f"  [Delete] Attempting to remove existing store files: {faiss_path}, {pkl_path}")
                     if faiss_path.exists():
                         os.remove(faiss_path)
                         print("    [Delete] Removed index.faiss")
                     if pkl_path.exists():
                         os.remove(pkl_path)
                         print("    [Delete] Removed index.pkl")
                     rebuild_successful = True
                 except Exception as clear_error:
                     print(f"  [Delete] Error clearing vector store files: {clear_error}")
                     rebuild_successful = False
        else: # No documents left in the index
            print("  [Delete] No documents left in index. Clearing vector store.")
            try:
                faiss_path = VECTORSTORE_DIR / "index.faiss"
                pkl_path = VECTORSTORE_DIR / "index.pkl"
                print(f"  [Delete] Attempting to remove existing store files: {faiss_path}, {pkl_path}")
                if faiss_path.exists():
                    os.remove(faiss_path)
                    print("    [Delete] Removed index.faiss")
                if pkl_path.exists():
                    os.remove(pkl_path)
                    print("    [Delete] Removed index.pkl")
                rebuild_successful = True
            except Exception as clear_error:
                print(f"  [Delete] Error clearing vector store files: {clear_error}")
                rebuild_successful = False

        # Clear the in-memory vectorstore instance in the retriever
        rag_retriever.vectorstore = None
        print("  [Delete] Cleared in-memory vector store instance.")

    except Exception as e:
        print(f"  [Delete] Error during vector store rebuild for deletion of {doc_id}: {e}")
        traceback.print_exc()
        rebuild_successful = False

    # --- Return Response ---
    detail_message = f"Document ID '{doc_id}' removed from index."
    if file_deleted:
        detail_message += " Original file deleted."
    else:
        detail_message += " Original file not found or deletion failed."

    if rebuild_successful:
        detail_message += " Vector store rebuilt/cleared."
    else:
        detail_message += " Vector store rebuild failed."

    print(f"--- Finished Deletion Process for doc_id: {doc_id} ---")
    return JSONResponse({"status": "success", "detail": detail_message}, status_code=200)

# --- Main execution (for running with `python app/main.py`) ---
# Note: Typically run with `uvicorn app.main:app --reload` from the chatbot-RAG directory
if __name__ == "__main__":
    # Make sure we're running from the project root for imports to work correctly
    project_root = Path(__file__).parent.parent
    os.chdir(project_root) 
    print(f"Running uvicorn for {__name__}...")
    print(f"Current working directory: {os.getcwd()}") # Should be chatbot-RAG
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True) 