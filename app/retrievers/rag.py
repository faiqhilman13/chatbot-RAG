from langchain_community.vectorstores import FAISS
from app.config import EMBEDDING_MODEL, VECTORSTORE_DIR, RETRIEVAL_K
import os
import pickle
from typing import List, Tuple, Optional, Dict, Any
from langchain.schema import Document

class RAGRetriever:
    def __init__(self):
        """Initialize the RAG retriever"""
        self.vectorstore = None
        self.embedding_model = EMBEDDING_MODEL
        self.vectorstore_path = VECTORSTORE_DIR
        
    def load_vectorstore(self) -> bool:
        """Load the vectorstore from disk if it exists"""
        if self.vectorstore:
            return True
            
        if not self.embedding_model:
            print("Embedding model not available")
            return False
            
        try:
            index_path = os.path.join(self.vectorstore_path, "index.faiss")
            if os.path.exists(index_path):
                self.vectorstore = FAISS.load_local(
                    self.vectorstore_path, 
                    self.embedding_model, 
                    allow_dangerous_deserialization=True
                )
                print(f"Loaded vectorstore from {self.vectorstore_path}")
                return True
            else:
                print(f"No existing vectorstore found at {self.vectorstore_path}")
                return False
        except Exception as e:
            print(f"Error loading vectorstore: {str(e)}")
            return False
    
    def build_vectorstore(self, docs) -> bool:
        """Build a new vectorstore from documents"""
        if not self.embedding_model:
            print("Embedding model not available")
            return False
            
        if not docs:
            print("No documents provided for building vectorstore")
            return False
            
        try:
            print(f"Building vectorstore with {len(docs)} documents")
            self.vectorstore = FAISS.from_documents(docs, self.embedding_model)
            self.save_vectorstore()
            return True
        except Exception as e:
            print(f"Error building vectorstore: {str(e)}")
            return False
    
    def save_vectorstore(self) -> bool:
        """Save the vectorstore to disk"""
        if not self.vectorstore:
            print("No vectorstore to save")
            return False
            
        try:
            self.vectorstore.save_local(self.vectorstore_path)
            print(f"Saved vectorstore to {self.vectorstore_path}")
            return True
        except Exception as e:
            print(f"Error saving vectorstore: {str(e)}")
            return False
    
    def retrieve_context(self, question: str, k: int = None) -> List[Document]:
        """Retrieve relevant document chunks for a question.
        
        Args:
            question: The question to retrieve context for.
            k: Number of documents/chunks to retrieve.
            
        Returns:
            A list of relevant Document objects.
        """
        if not self.vectorstore:
            if not self.load_vectorstore():
                print("[Retriever] Vectorstore not loaded, returning empty list.")
                return []
                
        if k is None:
            k = RETRIEVAL_K
            
        try:
            retriever = self.vectorstore.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": k}
            )
            # Retrieve the full Document objects
            relevant_docs: List[Document] = retriever.get_relevant_documents(question)
            
            print(f"[Retriever] Retrieved {len(relevant_docs)} chunks for question.")
            # Optionally print retrieved sources/metadata for debugging
            # for i, doc in enumerate(relevant_docs):
            #     print(f"  - Doc {i}: {doc.metadata}")
            
            # No source_filter logic needed here anymore
            
            # Return the list of documents directly
            return relevant_docs
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return []

# Create a singleton instance
rag_retriever = RAGRetriever() 