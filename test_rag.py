import requests
import os
import time
from urllib.parse import urljoin

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    response = requests.get(urljoin(BASE_URL, "/health"))
    print(f"Health check status: {response.status_code}")
    print(f"Health check response: {response.json()}")
    return response.status_code == 200

def create_test_pdf():
    """Create a simple test PDF file"""
    from reportlab.pdfgen import canvas
    
    pdf_file = "test_document.pdf"
    c = canvas.Canvas(pdf_file)
    
    # Add some test content
    c.drawString(100, 750, "Test Document for RAG Chatbot")
    c.drawString(100, 700, "This is a sample PDF document created for testing purposes.")
    c.drawString(100, 650, "It contains information about artificial intelligence.")
    c.drawString(100, 600, "Artificial intelligence (AI) is intelligence demonstrated by machines.")
    c.drawString(100, 550, "AI applications include advanced web search engines, recommendation systems,")
    c.drawString(100, 500, "understanding human speech, self-driving cars, and automated decision-making.")
    c.save()
    
    # Verify file was created
    if os.path.exists(pdf_file):
        print(f"Created test PDF: {pdf_file}")
        return pdf_file
    else:
        print("Failed to create test PDF")
        return None

def upload_document_to_path(file_path, title="Test Document"):
    """Upload a document to the path endpoint"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    # Use the upload_and_process endpoint from the ask.py router
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(file_path)
        
        # The endpoint expects the file_path parameter directly, not in a JSON
        response = requests.post(
            urljoin(BASE_URL, "/upload_and_process"),
            params={"file_path": abs_path}  # Using query parameters instead of JSON
        )
        
        if response.status_code == 200:
            print(f"Upload successful via path: {response.json()}")
            return True
        else:
            print(f"Upload failed via path: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Upload error via path: {str(e)}")
        return False

def upload_document(file_path, title="Test Document"):
    """Upload a document to the API directly"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    try:
        # Try first with the file upload endpoint
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "application/pdf")}
            data = {"title": title}
            
            response = requests.post(
                urljoin(BASE_URL, "/upload"), 
                files=files, 
                data=data
            )
        
        if response.status_code == 200:
            print(f"Upload successful: {response.json()}")
            return True
        elif response.status_code == 404:
            # If 404, try the path upload method
            print("Upload endpoint not found, trying path method...")
            return upload_document_to_path(file_path, title)
        else:
            print(f"Upload failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Upload error: {str(e)}")
        # Try the path method as a fallback
        print("Trying path method as fallback...")
        return upload_document_to_path(file_path, title)

def list_documents():
    """List all documents in the API"""
    try:
        response = requests.get(urljoin(BASE_URL, "/documents"))
        if response.status_code == 200:
            documents = response.json().get("documents", [])
            print(f"Documents: {len(documents)}")
            for doc in documents:
                print(f"  - {doc.get('title')} ({doc.get('filename')})")
            return documents
        else:
            print(f"List documents failed: {response.status_code}")
            print(response.text)
            return []
    except Exception as e:
        print(f"List documents error: {str(e)}")
        return []

def ask_question(question):
    """Ask a question to the API"""
    data = {"question": question}
    try:
        response = requests.post(urljoin(BASE_URL, "/ask"), json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nQuestion: {result['question']}")
            print(f"Answer: {result['answer']}")
            print(f"Sources: {', '.join(result['sources']) if result['sources'] else 'None'}")
            return True
        else:
            print(f"Question failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Question error: {str(e)}")
        return False

def main():
    """Run the test script"""
    print("Testing RAG Chatbot API...")
    
    # Check health
    if not test_health():
        print("Health check failed. Exiting.")
        return
    
    # List existing documents
    print("\nExisting documents:")
    list_documents()
    
    # Create test PDF
    try:
        pdf_file = create_test_pdf()
        if not pdf_file:
            print("Failed to create test PDF. Exiting.")
            return
        
        # Upload document
        print("\nUploading document...")
        if not upload_document(pdf_file):
            print("Document upload failed. Exiting.")
            return
        
        # Wait for processing
        print("Waiting for document processing...")
        time.sleep(2)
        
        # List documents after upload
        print("\nDocuments after upload:")
        list_documents()
        
        # Ask questions
        questions = [
            "What is artificial intelligence?",
            "What are some applications of AI?",
            "What is the meaning of life?",  # Should not be in the document
        ]
        
        for question in questions:
            ask_question(question)
            time.sleep(1)
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
    finally:
        # Clean up test file
        if 'pdf_file' in locals() and os.path.exists(pdf_file):
            os.remove(pdf_file)
            print(f"Removed test file: {pdf_file}")

if __name__ == "__main__":
    main() 