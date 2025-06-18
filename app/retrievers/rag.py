from langchain_community.vectorstores import FAISS
from app.config import EMBEDDING_MODEL, VECTORSTORE_DIR, RETRIEVAL_K, RETRIEVAL_CANDIDATES, CROSS_ENCODER_MODEL
import os
import pickle
from typing import List, Tuple, Optional, Dict, Any, Union
from langchain.schema import Document

class RAGRetriever:
    def __init__(self):
        """Initialize the RAG retriever"""
        self.vectorstore = None
        self.embedding_model = EMBEDDING_MODEL
        self.vectorstore_path = VECTORSTORE_DIR
        self.cross_encoder = CROSS_ENCODER_MODEL
        
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
    
    def _rerank_with_cross_encoder(self, question: str, docs: List[Document], k: int) -> List[Document]:
        """Rerank documents using cross-encoder model.
        
        Args:
            question: The question to compare documents against.
            docs: List of documents to rerank.
            k: Number of top documents to return.
            
        Returns:
            A list of reranked documents, limited to top k.
        """
        if not self.cross_encoder or not docs:
            return docs[:k] if docs else []
            
        try:
            # Prepare document-query pairs for cross-encoder
            pairs = [(question, doc.page_content) for doc in docs]
            
            # Get similarity scores
            scores = self.cross_encoder.predict(pairs)
            
            # Create (score, document) pairs
            scored_docs = list(zip(scores, docs))
            
            # Sort by score in descending order
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            
            # Extract just the documents, now in sorted order
            reranked_docs = [doc for _, doc in scored_docs]
            
            print(f"[Reranker] Reranked {len(docs)} documents, returning top {k}")
            return reranked_docs[:k]
        except Exception as e:
            print(f"Error during cross-encoder reranking: {str(e)}")
            # Fall back to original order if reranking fails
            return docs[:k]
    
    def _filter_documents_by_metadata(self, docs: List[Document], 
                                     filter_criteria: Dict[str, Any]) -> List[Document]:
        """Filter documents based on metadata criteria.
        
        Args:
            docs: List of documents to filter
            filter_criteria: Dictionary of metadata keys and values to filter by
                             Can include: doc_id, title, source, etc.
        
        Returns:
            Filtered list of documents
        """
        if not filter_criteria:
            return docs
            
        filtered_docs = []
        for doc in docs:
            match = True
            for key, value in filter_criteria.items():
                # Handle exact match
                if isinstance(value, str) and key in doc.metadata:
                    if value.lower() != str(doc.metadata.get(key, "")).lower():
                        match = False
                        break
                # Handle list of possible values
                elif isinstance(value, list) and key in doc.metadata:
                    if str(doc.metadata.get(key, "")).lower() not in [v.lower() for v in value]:
                        match = False
                        break
                # Handle missing metadata key
                elif key not in doc.metadata:
                    match = False
                    break
            
            if match:
                filtered_docs.append(doc)
                
        print(f"[Filter] Filtered {len(docs)} documents to {len(filtered_docs)} based on criteria: {filter_criteria}")
        return filtered_docs
    
    def _detect_query_intent(self, question: str) -> Dict[str, Any]:
        """Detect query intent to automatically apply filters.
        
        Args:
            question: The question to analyze
            
        Returns:
            Dictionary of detected metadata filters
        """
        filters = {}
        
        # Simple keyword-based intent detection
        question_lower = question.lower()
        
        # Person name detection for CV/resume queries
        person_keywords = ["cv", "resume", "faiq", "hilman", "experience", "education", "skills", "work history"]
        if any(keyword in question_lower for keyword in person_keywords):
            # Look for CV/resume documents
            filters["title"] = ["cv", "resume", "faiq cv", "faiq hilman", "faiq hilman cv"]
        
        # Financial document detection
        financial_keywords = ["financial", "report", "earnings", "revenue", "profit", "loss", "balance", "income", "cash flow", "tesla", "fy24"]
        if any(keyword in question_lower for keyword in financial_keywords):
            filters["title"] = ["tesla fy24", "financial report", "earnings report"]
            
        print(f"[Intent] Detected query intent filters: {filters}")
        return filters
    
    def retrieve_context(self, question: str, k: int = None, 
                        filter_criteria: Dict[str, Any] = None,
                        auto_filter: bool = True) -> List[Document]:
        """Retrieve relevant document chunks for a question.
        
        Args:
            question: The question to retrieve context for.
            k: Number of documents/chunks to retrieve after reranking.
            filter_criteria: Optional dictionary of metadata filters to apply
            auto_filter: Whether to automatically detect query intent and apply filters
            
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
            # Get more candidates than we need for reranking
            candidates_k = RETRIEVAL_CANDIDATES if self.cross_encoder else k
            
            # Apply automatic filtering if enabled
            if auto_filter and not filter_criteria:
                filter_criteria = self._detect_query_intent(question)
            
            retriever = self.vectorstore.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": candidates_k}
            )
            # Retrieve the full Document objects
            candidate_docs: List[Document] = retriever.get_relevant_documents(question)
            
            print(f"[Retriever] Retrieved {len(candidate_docs)} candidate chunks for question.")
            
            # Apply metadata filtering if criteria provided
            if filter_criteria:
                candidate_docs = self._filter_documents_by_metadata(candidate_docs, filter_criteria)
                print(f"[Retriever] After filtering: {len(candidate_docs)} documents remain.")
                
                # If we filtered out too many, try to get more candidates
                if len(candidate_docs) < k and len(candidate_docs) > 0:
                    print(f"[Retriever] Too few documents after filtering, retrieving more candidates...")
                    # Increase candidates to try to get enough after filtering
                    more_retriever = self.vectorstore.as_retriever(
                        search_type="similarity", 
                        search_kwargs={"k": candidates_k * 3}  # Try with 3x more candidates
                    )
                    more_candidates = more_retriever.get_relevant_documents(question)
                    filtered_more = self._filter_documents_by_metadata(more_candidates, filter_criteria)
                    
                    # Only use the expanded results if we actually got more
                    if len(filtered_more) > len(candidate_docs):
                        candidate_docs = filtered_more
                        print(f"[Retriever] Retrieved {len(candidate_docs)} documents after expanded search.")
            
            # Apply reranking if cross-encoder is available
            if self.cross_encoder and len(candidate_docs) > k:
                relevant_docs = self._rerank_with_cross_encoder(question, candidate_docs, k)
            else:
                relevant_docs = candidate_docs[:k]
                
            print(f"[Retriever] Final document count: {len(relevant_docs)}")
            
            # Return the list of documents directly
            return relevant_docs
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return []

# Create a singleton instance
rag_retriever = RAGRetriever() 