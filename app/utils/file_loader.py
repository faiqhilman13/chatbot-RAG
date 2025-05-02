from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
from app.config import CHUNK_SIZE, CHUNK_OVERLAP
from typing import Iterable, Tuple, Optional

def extract_text_from_pdf(file_path: str) -> Iterable[Tuple[str, int]]:
    """Extract text from PDF, yielding (page_content, page_number) tuples."""
    try:
        with open(file_path, "rb") as file:
            pdf = PdfReader(file)
            print(f"[PDF Load] Processing {len(pdf.pages)} pages from {os.path.basename(file_path)}")
            for i, page in enumerate(pdf.pages):
                content = page.extract_text()
                if content:
                    yield content, i + 1 # Yield content and 1-based page number
                else:
                    print(f"[PDF Load] No text found on page {i+1}")
    except Exception as e:
        print(f"Error extracting text from {file_path}: {str(e)}")
        # Yield nothing if error

def chunk_text(text: str, metadata: dict) -> list[Document]:
    """Split text into chunks with the specified size and overlap."""
    if not text:
        return []
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    # create_documents expects a list of texts and list of metadatas
    # Here we process one page text at a time
    return splitter.create_documents([text], metadatas=[metadata])

def prepare_documents(file_paths: list[str], title: Optional[str] = None, doc_id: Optional[str] = None) -> list[Document]:
    """Extract text page by page, chunk, and add metadata including page number."""
    all_chunks = []
    if not isinstance(file_paths, list):
        file_paths = [file_paths] # Allow single file path input
        
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        filename = os.path.basename(file_path)
        print(f"[Prepare] Processing file: {filename} (ID: {doc_id}, Title: {title})")
        
        # Process page by page
        for page_content, page_num in extract_text_from_pdf(file_path):
            # Create metadata for this specific page
            page_metadata = {
                "source": filename,
                "path": file_path, # Keep original path
                "page": page_num, # Add page number
                "title": title or filename, # Use title or fallback to filename
                "doc_id": doc_id or "unknown" # Use provided doc_id or fallback
            }
            
            # Chunk the text from this page with its specific metadata
            page_chunks = chunk_text(page_content, page_metadata)
            all_chunks.extend(page_chunks)
            # print(f"  - Prepared {len(page_chunks)} chunks for page {page_num}") # Verbose
        
        print(f"[Prepare] Finished file {filename}, total chunks: {len(all_chunks)}")
            
    return all_chunks

def get_all_documents(doc_folder: str) -> list[Document]:
    """Load all PDF documents from a folder and prepare chunks."""
    all_docs = []
    if not os.path.exists(doc_folder):
        print(f"Document folder not found: {doc_folder}")
        return all_docs
    
    pdf_files = [os.path.join(doc_folder, f) for f in os.listdir(doc_folder) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"No PDF files found in {doc_folder}")
        return all_docs
        
    # Process all files together? Or one by one? 
    # Let's stick to one by one for simplicity, assuming prepare_documents handles list
    for file_path in pdf_files:
        try:
            # prepare_documents now handles title/doc_id, but we don't have them here.
            # It will use filename as title and 'unknown' as doc_id.
            # It expects a list, so pass [file_path]
            docs = prepare_documents([file_path]) 
            all_docs.extend(docs)
            # This print might be redundant now as prepare_documents logs
            # print(f"Added {len(docs)} chunks from {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)} in get_all_documents: {str(e)}")
            
    print(f"[get_all_docs] Loaded {len(all_docs)} total chunks from {len(pdf_files)} files.")
    return all_docs 