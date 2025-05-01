from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file"""
    text = ""
    try:
        with open(file_path, "rb") as file:
            pdf = PdfReader(file)
            for i, page in enumerate(pdf.pages):
                content = page.extract_text()
                if content:
                    text += f"\n--- Page {i+1} ---\n{content}"
        return text
    except Exception as e:
        print(f"Error extracting text from {file_path}: {str(e)}")
        return ""

def chunk_text(text, metadata=None):
    """Split text into chunks with the specified size and overlap"""
    if not text:
        return []
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    
    if metadata:
        return splitter.create_documents([text], [metadata])
    else:
        return splitter.split_text(text)

def prepare_documents(file_path):
    """Extract text from PDF and prepare document chunks with metadata"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
        
    filename = os.path.basename(file_path)
    raw_text = extract_text_from_pdf(file_path)
    
    if not raw_text:
        print(f"No text extracted from {file_path}")
        return []
    
    metadata = {"source": filename, "path": file_path}
    return chunk_text(raw_text, metadata)

def get_all_documents(doc_folder):
    """Get all documents from the documents folder"""
    all_docs = []
    
    if not os.path.exists(doc_folder):
        print(f"Document folder not found: {doc_folder}")
        return all_docs
    
    for filename in os.listdir(doc_folder):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(doc_folder, filename)
            try:
                docs = prepare_documents(file_path)
                all_docs.extend(docs)
                print(f"Added {len(docs)} chunks from {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    return all_docs 