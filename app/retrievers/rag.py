from langchain_community.vectorstores import FAISS
from app.config import EMBEDDING_MODEL, VECTORSTORE_DIR, RETRIEVAL_K
from app.utils.entity_extractor import extract_named_entities
import os
import pickle
from typing import List, Tuple, Optional, Dict, Any

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
    
    def retrieve_context(self, question: str, k: int = None) -> Tuple[str, List[str]]:
        """
        Retrieve context for a question, with entity filtering
        
        Args:
            question (str): The question to retrieve context for
            k (int, optional): Number of documents to retrieve
            
        Returns:
            Tuple[str, List[str]]: Retrieved context and list of source documents
        """
        if not self.vectorstore:
            if not self.load_vectorstore():
                return "", []
                
        if k is None:
            k = RETRIEVAL_K
            
        try:
            # Extract named entities from question
            entities = extract_named_entities(question)
            
            # Get more documents than needed for filtering
            retriever = self.vectorstore.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": k * 2}  # Get more docs for filtering
            )
            docs = retriever.get_relevant_documents(question)
            
            if entities:
                # Filter docs that contain any of the entities
                filtered_docs = []
                entities_lower = [e.lower() for e in entities]
                
                for doc in docs:
                    content_lower = doc.page_content.lower()
                    if any(entity in content_lower for entity in entities_lower):
                        filtered_docs.append(doc)
                
                # Use filtered docs if any match, otherwise fall back to original
                if filtered_docs:
                    docs = filtered_docs[:k]
                else:
                    docs = docs[:k]
            else:
                # No entities found, use top k docs
                docs = docs[:k]
            
            # Format context with source attribution
            context_parts = []
            sources = []
            
            for doc in docs:
                source = doc.metadata.get("source", "unknown")
                content = doc.page_content.strip()
                context_parts.append(f"[From: {source}]\n{content}")
                
                if source not in sources:
                    sources.append(source)
            
            context = "\n\n".join(context_parts)
            return context, sources
            
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return "", []

# Create a singleton instance
rag_retriever = RAGRetriever() 