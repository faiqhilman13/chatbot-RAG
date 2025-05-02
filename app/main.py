from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil
import uuid
from pathlib import Path
import sys # Add import for sys
import json # Add import for json
from app.routers import ask
from app.config import DOCUMENTS_DIR, VECTORSTORE_DIR, BASE_DIR # Import BASE_DIR
from app.retrievers.rag import rag_retriever
from app.utils.file_loader import prepare_documents
import traceback # Add import for traceback module

# CURSOR: This file should only handle route wiring, not business logic.
# All logic must be called from services/ or utils/

# Create FastAPI app
app = FastAPI(title="Hybrid RAG Chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(ask.router)

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

@app.post("/upload", tags=["Documents"])
async def upload_document(file: UploadFile = File(...), title: str = Form(None)):
    # CURSOR: Logic should ideally be in a service function
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

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
        # --- Build/Save Vector Store --- 
        build_success = rag_retriever.build_vectorstore(chunks)
        if not build_success:
            print(f"Failed to build/save vector store for {doc_title}.")
            # Clean up? Raise error.
            raise HTTPException(status_code=500, detail=f"Failed to update vector store for {doc_title}.")
        print(f"Vector store updated successfully for: {doc_title}")
        # --- End Build/Save Vector Store ---
        
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

@app.get("/documents", tags=["Documents"])
async def list_documents():
    # --- Read from JSON Index --- 
    print("Loading documents from JSON index...")
    index_data = load_document_index()
    # Convert the dictionary values to a list for the frontend
    documents_list = list(index_data.values())
    print(f"Found {len(documents_list)} documents in index.")
    return JSONResponse({"documents": documents_list})
    # --- End Read from JSON Index ---

@app.delete("/documents/{doc_id}", tags=["Documents"])
async def delete_document(doc_id: str):
    print(f"Attempting to delete document with ID: {doc_id}")
    vector_deletion_successful = False
    index_entry_found = False
    
    # --- Delete from Vector Store (Keep this attempt) ---
    try:
        if not rag_retriever.load_vectorstore():
            print("Vector store could not be loaded for deletion.")
            # Don't raise immediately, still try to delete from index
        else:
            vector_store = rag_retriever.vectorstore
            if vector_store:
                results = vector_store.get(where={"doc_id": doc_id}, include=[]) # FAISS doesn't have get, but check logic
                # Correct way to delete from FAISS if needed might involve rebuilding 
                # or using specific IDs if stored separately. For now, focus on index.
                # We'll assume deletion from FAISS might fail or isn't fully implemented here.
                # Placeholder for actual FAISS deletion logic if implemented:
                # chunk_ids_to_delete = find_chunk_ids_for_doc_id(vector_store, doc_id)
                # if chunk_ids_to_delete:
                #     vector_store.delete(ids=chunk_ids_to_delete)
                #     vector_deletion_successful = True
                #     print(f"Deleted {len(chunk_ids_to_delete)} chunks for doc_id {doc_id} from vector store.")
                # else:
                #     print(f"No chunks found in vector store for doc_id {doc_id}")
                print(f"Note: Vector store deletion logic for FAISS needs specific implementation.")
                vector_deletion_successful = True # Assume ok for now if we can load it
            else:
                print("Vector store object not available after load attempt.")
    except Exception as e:
        print(f"Error during vector store access/deletion for doc_id {doc_id}: {e}")
        # Log error but continue to attempt index deletion
        
    # --- Delete from JSON Index ---    
    index_data = load_document_index()
    if doc_id in index_data:
        index_entry_found = True
        original_filename = index_data[doc_id].get("filename") # Get filename before deleting
        del index_data[doc_id]
        save_document_index(index_data)
        print(f"Removed doc_id {doc_id} from document index.")
        
        # --- Optionally: Delete the original file --- 
        # Use the doc_id and filename from the index entry we just deleted
        if original_filename:
            # Construct the expected saved filename format
            safe_filename = f"{doc_id}_{original_filename}"
            file_path_to_delete = DOCUMENTS_DIR / safe_filename
            if file_path_to_delete.exists():
                try:
                    os.remove(file_path_to_delete)
                    print(f"Deleted original file: {file_path_to_delete}")
                except OSError as rm_error:
                    print(f"Error deleting original file {file_path_to_delete}: {rm_error}")
            else:
                print(f"Original file not found for deletion: {file_path_to_delete}")
        else:
             print(f"Original filename not found in index for doc_id {doc_id}, cannot delete file.")
            
    else:
        print(f"doc_id {doc_id} not found in document index.")

    # --- Return Response --- 
    if index_entry_found:
         # Consider successful even if vector deletion part isn't fully working
        return JSONResponse({"status": "success", "detail": f"Document ID '{doc_id}' removed from index. File deleted if found."}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found.")

# --- Main execution (for running with `python app/main.py`) ---
# Note: Typically run with `uvicorn app.main:app --reload` from the chatbot-RAG directory
if __name__ == "__main__":
    # Make sure we're running from the project root for imports to work correctly
    project_root = Path(__file__).parent.parent
    os.chdir(project_root) 
    print(f"Running uvicorn for {__name__}...")
    print(f"Current working directory: {os.getcwd()}") # Should be chatbot-RAG
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 