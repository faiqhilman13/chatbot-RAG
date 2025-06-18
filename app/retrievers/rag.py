from langchain_community.vectorstores import FAISS
from app.config import EMBEDDING_MODEL, VECTORSTORE_DIR, RETRIEVAL_K, RETRIEVAL_CANDIDATES, CROSS_ENCODER_MODEL
from app.utils.query_analyzer import query_analyzer, QueryAnalysis
from app.utils.source_attribution import source_attribution_manager
from app.utils.hybrid_retrieval import HybridRetriever, RetrievalResult
import os
import pickle
from typing import List, Tuple, Optional, Dict, Any, Union
from langchain.schema import Document
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RAGRetriever:
    def __init__(self):
        """Initialize the RAG retriever"""
        self.vectorstore = None
        self.embedding_model = EMBEDDING_MODEL
        self.vectorstore_path = VECTORSTORE_DIR
        self.cross_encoder = CROSS_ENCODER_MODEL
        self.query_analyzer = query_analyzer
        self.source_attribution = source_attribution_manager
        self.hybrid_retriever = None
        
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
            
            # Initialize hybrid retriever with document corpus
            self._initialize_hybrid_retriever(docs)
            
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
    
    def _initialize_hybrid_retriever(self, docs):
        """Initialize hybrid retriever with document corpus"""
        try:
            document_texts = [doc.page_content for doc in docs]
            document_metadata = [doc.metadata for doc in docs]
            
            self.hybrid_retriever = HybridRetriever(
                dense_weight=0.7,
                sparse_weight=0.3,
                fallback_threshold=0.1
            )
            
            self.hybrid_retriever.fit(document_texts, document_metadata)
            print(f"Initialized hybrid retriever with {len(document_texts)} documents")
            
        except Exception as e:
            print(f"Error initializing hybrid retriever: {str(e)}")
            self.hybrid_retriever = None
    
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
    
    def _cluster_documents_post_rerank(self, docs: List[Document], k: int) -> List[Document]:
        """Cluster documents after reranking to prevent context mixing using semantic similarity.
        
        Args:
            docs: List of reranked documents.
            k: Number of documents to return.
            
        Returns:
            Documents from the most semantically cohesive cluster.
        """
        if len(docs) <= k:
            return docs
            
        try:
            # Get embeddings for all document contents using the same embedding model
            doc_texts = [doc.page_content for doc in docs]
            
            # Create embeddings using the same model used for vector store
            if not self.embedding_model:
                print("[Clustering] No embedding model available, falling back to original order")
                return docs[:k]
            
            # Get embeddings for semantic clustering
            embeddings = self.embedding_model.embed_documents(doc_texts)
            embeddings = np.array(embeddings)
            
            # Calculate cosine similarity matrix
            similarity_matrix = cosine_similarity(embeddings)
            
            # Convert similarity to distance for clustering (1 - similarity)
            distance_matrix = 1 - similarity_matrix
            
            # Use DBSCAN clustering on semantic similarity
            clustering = DBSCAN(eps=0.3, min_samples=2, metric='precomputed')
            cluster_labels = clustering.fit_predict(distance_matrix)
            
            # Find the largest cluster (most coherent group)
            unique_labels, counts = np.unique(cluster_labels[cluster_labels >= 0], return_counts=True)
            
            if len(unique_labels) > 0:
                largest_cluster_label = unique_labels[np.argmax(counts)]
                clustered_docs = [doc for i, doc in enumerate(docs) if cluster_labels[i] == largest_cluster_label]
                
                print(f"[Semantic Clustering] Found {len(unique_labels)} clusters, selecting largest with {len(clustered_docs)} documents")
                
                # Return documents from the largest cluster, up to k
                return clustered_docs[:k]
            else:
                print(f"[Semantic Clustering] No coherent clusters found, returning top {k} documents")
                return docs[:k]
                
        except Exception as e:
            print(f"[Semantic Clustering] Error during clustering: {str(e)}, falling back to original order")
            return docs[:k]
    
    def _filter_by_keyword_overlap(self, question: str, docs: List[Document], min_overlap: float = 0.1) -> List[Document]:
        """Filter documents by keyword overlap with the query (domain-agnostic).
        
        Args:
            question: The user's question.
            docs: List of documents to filter.
            min_overlap: Minimum keyword overlap ratio to keep a document.
            
        Returns:
            Documents with sufficient keyword overlap.
        """
        try:
            import re
            from collections import Counter
            
            # Normalize and tokenize query (remove stopwords, punctuation)
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
            
            # Company name aliases for better matching
            company_aliases = {
                'pricewaterhouse': ['pwc', 'pricewaterhousecoopers', 'price waterhouse coopers'],
                'pwc': ['pricewaterhouse', 'pricewaterhousecoopers', 'price waterhouse coopers'],
                'pricewaterhousecoopers': ['pwc', 'pricewaterhouse', 'price waterhouse coopers'],
                'coopers': ['pwc', 'pricewaterhouse', 'pricewaterhousecoopers'],
                'ernst': ['ey', 'ernst young', 'ernstyoung'],
                'young': ['ey', 'ernst young', 'ernstyoung'],
                'ey': ['ernst', 'young', 'ernst young', 'ernstyoung']
            }
            
            # Extract meaningful keywords from query
            query_words = re.findall(r'\b[a-zA-Z]+\b', question.lower())
            query_keywords = [word for word in query_words if len(word) > 2 and word not in stopwords]
            
            # For education queries, expand keywords to include education-related terms
            education_terms = ["study", "studied", "university", "college", "school", "degree", "education"]
            if any(term in query_keywords for term in ["study", "studied", "xin", "yi"]):
                query_keywords.extend(["university", "college", "school", "degree", "education", "bachelor", "master"])
                query_keywords = list(set(query_keywords))  # Remove duplicates
            
            if not query_keywords:
                return docs  # If no keywords, return all docs
            
            filtered_docs = []
            for doc in docs:
                # Extract words from document content
                doc_words = re.findall(r'\b[a-zA-Z]+\b', doc.page_content.lower())
                doc_word_set = set(doc_words)
                
                # Calculate keyword overlap with alias expansion
                matching_keywords = []
                for kw in query_keywords:
                    # Direct match
                    if kw in doc_word_set:
                        matching_keywords.append(kw)
                    # Alias match
                    elif kw in company_aliases:
                        for alias in company_aliases[kw]:
                            # Check if alias exists in document (with spaces)
                            if alias in doc.page_content.lower() or any(a in doc_word_set for a in alias.split()):
                                matching_keywords.append(kw)
                                break
                
                # More lenient overlap calculation
                overlap_ratio = len(set(matching_keywords)) / len(query_keywords)
                
                if overlap_ratio >= min_overlap:
                    filtered_docs.append(doc)
                    
            print(f"[Keyword Filter] Filtered {len(docs)} to {len(filtered_docs)} docs with >{min_overlap:.0%} keyword overlap")
            
            # If too few docs pass filter, return original docs
            return filtered_docs if filtered_docs else docs
            
        except Exception as e:
            print(f"[Keyword Filter] Error during filtering: {str(e)}, returning original docs")
            return docs
    
    def _score_context_coherence(self, docs: List[Document], k: int) -> List[Document]:
        """Score and rerank documents based on inter-document semantic coherence.
        
        Args:
            docs: List of documents to score.
            k: Number of documents to return.
            
        Returns:
            Documents reranked by coherence score.
        """
        if len(docs) <= k:
            return docs
            
        try:
            if not self.embedding_model:
                return docs[:k]
            
            # Get embeddings for all documents
            doc_texts = [doc.page_content for doc in docs]
            embeddings = self.embedding_model.embed_documents(doc_texts)
            embeddings = np.array(embeddings)
            
            # Calculate coherence scores for each document
            coherence_scores = []
            for i, doc in enumerate(docs):
                # Calculate average similarity with all other documents
                similarities = []
                for j, other_doc in enumerate(docs):
                    if i != j:
                        sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                        similarities.append(sim)
                
                # Coherence score is the average similarity with other documents
                coherence_score = np.mean(similarities) if similarities else 0.0
                coherence_scores.append((coherence_score, doc))
            
            # Sort by coherence score (descending)
            coherence_scores.sort(key=lambda x: x[0], reverse=True)
            
            # Return top k most coherent documents
            coherent_docs = [doc for _, doc in coherence_scores[:k]]
            
            avg_coherence = np.mean([score for score, _ in coherence_scores[:k]])
            print(f"[Coherence] Reranked by coherence, avg score: {avg_coherence:.3f}")
            
            return coherent_docs
            
        except Exception as e:
            print(f"[Coherence] Error during coherence scoring: {str(e)}, returning original order")
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
        
        # Person name detection for CV/resume queries (expanded for company queries and education)
        person_keywords = ["cv", "resume", "faiq", "hilman", "xin", "yi", "chow", "experience", "education", "skills", "work history", "pricewaterhouse", "pwc", "coopers", "ernst", "young", "ey", "company", "job", "work", "done", "worked", "study", "studied", "university", "college", "school", "degree", "bachelor", "master", "diploma", "graduate", "graduation"]
        if any(keyword in question_lower for keyword in person_keywords):
            # Check if query mentions specific person and prioritize their CV
            if any(name in question_lower for name in ["xin", "yi", "chow"]):
                # Query specifically mentions Xin Yi - prioritize her CV only
                filters["title"] = ["chow cv", "xin yi cv", "xin yi", "chow"]
            elif any(name in question_lower for name in ["faiq", "hilman"]):
                # Query specifically mentions Faiq - prioritize his CV only  
                filters["title"] = ["cv", "resume", "faiq cv", "faiq hilman", "faiq hilman cv"]
            else:
                # General CV query - search all CVs
                filters["title"] = ["cv", "resume", "faiq cv", "faiq hilman", "faiq hilman cv", "chow cv", "xin yi cv", "xin yi", "chow"]
        
        # Financial document detection
        financial_keywords = ["financial", "report", "earnings", "revenue", "profit", "loss", "balance", "income", "cash flow", "tesla", "fy24"]
        if any(keyword in question_lower for keyword in financial_keywords):
            filters["title"] = ["tesla fy24", "financial report", "earnings report"]
            
        print(f"[Intent] Detected query intent filters: {filters}")
        return filters
    
    def retrieve_context(self, question: str, k: int = None, 
                        filter_criteria: Dict[str, Any] = None,
                        auto_filter: bool = True,
                        use_adaptive_retrieval: bool = True) -> List[Document]:
        """Retrieve relevant document chunks for a question with adaptive intelligence.
        
        Args:
            question: The question to retrieve context for.
            k: Number of documents/chunks to retrieve after reranking.
            filter_criteria: Optional dictionary of metadata filters to apply
            auto_filter: Whether to automatically detect query intent and apply filters
            use_adaptive_retrieval: Whether to use adaptive retrieval intelligence
            
        Returns:
            A list of relevant Document objects with enhanced source attribution.
        """
        if not self.vectorstore:
            if not self.load_vectorstore():
                print("[Retriever] Vectorstore not loaded, returning empty list.")
                return []
        
        # 🧠 ADAPTIVE RETRIEVAL INTELLIGENCE
        if use_adaptive_retrieval:
            # Analyze query to determine optimal parameters
            query_analysis = self.query_analyzer.analyze_query(question)
            
            # Use adaptive K if not explicitly provided
            if k is None:
                k = query_analysis.optimal_k
                print(f"[AdaptiveRetrieval] Using adaptive K={k} for {query_analysis.query_type.value} query with {query_analysis.complexity.value} complexity")
            
            # Note: Adaptive chunk size would require re-chunking documents
            # For now, we'll use this information for future optimizations
            print(f"[AdaptiveRetrieval] Recommended chunk size: {query_analysis.chunk_size}, overlap: {query_analysis.chunk_overlap}")
        else:
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
            
            # 🌐 HYBRID RETRIEVAL & FALLBACK MECHANISMS
            # Check if we should use hybrid retrieval fallback
            if self.hybrid_retriever and candidate_docs:
                # Get dense scores for fallback evaluation
                dense_scores = []
                for doc in candidate_docs:
                    if hasattr(doc, 'metadata') and 'score' in doc.metadata:
                        dense_scores.append(doc.metadata['score'])
                    else:
                        # Approximate score based on position (first doc gets highest score)
                        dense_scores.append(1.0 - (candidate_docs.index(doc) / len(candidate_docs)))
                
                # Create (index, score) pairs for hybrid retrieval
                dense_results = [(i, score) for i, score in enumerate(dense_scores)]
                
                # Use hybrid retrieval with fallback
                hybrid_results = self.hybrid_retriever.search_with_fallback(
                    dense_results, question, top_k=candidates_k
                )
                
                # Convert hybrid results back to Document objects
                if hybrid_results:
                    hybrid_docs = []
                    for result in hybrid_results:
                        idx = int(result.chunk_id)
                        if idx < len(candidate_docs):
                            doc = candidate_docs[idx]
                            # Add hybrid scores to metadata
                            doc.metadata.update({
                                'dense_score': result.dense_score,
                                'sparse_score': result.sparse_score,
                                'hybrid_score': result.hybrid_score,
                                'retrieval_method': result.retrieval_method
                            })
                            hybrid_docs.append(doc)
                    
                    candidate_docs = hybrid_docs
                    print(f"[HybridRetrieval] Applied {hybrid_results[0].retrieval_method} retrieval strategy")
            
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
                relevant_docs = self._rerank_with_cross_encoder(question, candidate_docs, min(k * 2, len(candidate_docs)))
            else:
                relevant_docs = candidate_docs[:min(k * 2, len(candidate_docs))]
            
            # Domain-agnostic accuracy improvements pipeline:
            
            # 1. Apply keyword overlap filtering first (removes obviously unrelated chunks)
            # Use more lenient threshold for education/personal queries
            education_keywords = ["study", "studied", "university", "college", "school", "degree", "education", "graduate"]
            min_overlap_threshold = 0.01 if any(kw in question.lower() for kw in education_keywords) else 0.03
            relevant_docs = self._filter_by_keyword_overlap(question, relevant_docs, min_overlap=min_overlap_threshold)
            
            # 2. Apply semantic clustering to group related content 
            if len(relevant_docs) > k:
                relevant_docs = self._cluster_documents_post_rerank(relevant_docs, k * 2)  # Get larger cluster
            
            # 3. Apply coherence scoring for final ranking
            relevant_docs = self._score_context_coherence(relevant_docs, k)
                
            print(f"[Retriever] Final document count after domain-agnostic filtering: {len(relevant_docs)}")
            
            # 🧾 ENHANCED SOURCE ATTRIBUTION & CONTEXT MANAGEMENT (DISABLED FOR CLEAN OUTPUT)
            # Note: Source attribution temporarily disabled to improve answer readability
            # TODO: Re-enable with improved formatting after frontend monitoring dashboard is complete
            if False and use_adaptive_retrieval and relevant_docs:
                # Create anchored chunks with explicit source metadata
                relevant_docs = self.source_attribution.create_anchored_chunks(relevant_docs)
                
                # Detect cross-document references for better context awareness
                cross_refs = self.source_attribution.detect_cross_document_references(relevant_docs)
                if cross_refs:
                    print(f"[SourceAttribution] Cross-document references detected: {list(cross_refs.keys())}")
            
            # Return the list of documents directly
            return relevant_docs
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return []

# Create a singleton instance
rag_retriever = RAGRetriever() 