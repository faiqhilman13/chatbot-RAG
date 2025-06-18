"""
Hybrid Retrieval & Fallback Mechanisms

This module implements BM25 keyword search fallback, sparse-dense hybrid scoring,
and automatic retrieval strategy selection for improved retrieval accuracy.
"""

import re
import math
import logging
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter, defaultdict
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Result from hybrid retrieval with multiple scores"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    dense_score: float      # Vector similarity score
    sparse_score: float     # BM25 keyword score  
    hybrid_score: float     # Combined score
    retrieval_method: str   # "dense", "sparse", "hybrid"

class BM25Retriever:
    """BM25 (Best Matching 25) keyword-based retrieval implementation"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 retriever
        
        Args:
            k1: Controls term frequency saturation (1.2-2.0)
            b: Controls field length normalization (0.0-1.0)
        """
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_freqs = []
        self.idf = {}
        self.doc_lengths = []
        self.avgdl = 0
        self.corpus_metadata = []
        self.is_fitted = False
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization with normalization"""
        # Convert to lowercase and extract alphanumeric tokens
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def fit(self, corpus: List[str], metadata: List[Dict[str, Any]] = None):
        """
        Fit BM25 on document corpus
        
        Args:
            corpus: List of document strings
            metadata: Optional metadata for each document
        """
        self.corpus = corpus
        self.corpus_metadata = metadata or [{} for _ in corpus]
        
        # Tokenize all documents
        tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        
        # Calculate document frequencies
        self.doc_freqs = []
        for tokens in tokenized_corpus:
            self.doc_freqs.append(Counter(tokens))
        
        # Calculate document lengths
        self.doc_lengths = [len(tokens) for tokens in tokenized_corpus]
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        # Calculate IDF for each term
        df = defaultdict(int)
        for tokens in tokenized_corpus:
            for token in set(tokens):
                df[token] += 1
        
        self.idf = {}
        num_docs = len(corpus)
        for term, freq in df.items():
            self.idf[term] = math.log((num_docs - freq + 0.5) / (freq + 0.5))
        
        self.is_fitted = True
        logger.info(f"BM25 fitted on {num_docs} documents with {len(self.idf)} unique terms")
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Search using BM25 scoring
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of (doc_index, bm25_score) tuples sorted by score
        """
        if not self.is_fitted:
            raise ValueError("BM25 retriever must be fitted before searching")
        
        query_tokens = self._tokenize(query)
        scores = []
        
        for doc_idx, doc_freqs in enumerate(self.doc_freqs):
            score = 0.0
            doc_length = self.doc_lengths[doc_idx]
            
            for token in query_tokens:
                if token in doc_freqs:
                    tf = doc_freqs[token]
                    idf = self.idf.get(token, 0)
                    
                    # BM25 formula
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avgdl))
                    score += idf * (numerator / denominator)
            
            scores.append((doc_idx, score))
        
        # Sort by score (descending) and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

class HybridRetriever:
    """Hybrid retrieval system combining dense and sparse methods"""
    
    def __init__(self, 
                 embedding_model: SentenceTransformer,
                 dense_weight: float = 0.7,
                 sparse_weight: float = 0.3,
                 fallback_threshold: float = 0.1):
        """
        Initialize hybrid retriever
        
        Args:
            embedding_model: Pre-trained sentence transformer model
            dense_weight: Weight for dense (vector) retrieval scores
            sparse_weight: Weight for sparse (BM25) retrieval scores
            fallback_threshold: Minimum dense score to trigger BM25 fallback
        """
        self.embedding_model = embedding_model
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.fallback_threshold = fallback_threshold
        
        self.bm25 = BM25Retriever()
        self.document_embeddings = None
        self.documents = []
        self.metadata = []
        self.is_fitted = False
    
    def fit(self, documents: List[str], metadata: List[Dict[str, Any]] = None):
        """
        Fit hybrid retriever on document corpus
        
        Args:
            documents: List of document strings
            metadata: Optional metadata for each document
        """
        self.documents = documents
        self.metadata = metadata or [{} for _ in documents]
        
        # Fit BM25 retriever
        self.bm25.fit(documents, metadata)
        
        # Generate embeddings for dense retrieval
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        self.document_embeddings = self.embedding_model.encode(
            documents, 
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        self.is_fitted = True
        logger.info("Hybrid retriever fitted successfully")
    
    def _dense_search(self, query: str, top_k: int = 20) -> List[Tuple[int, float]]:
        """Perform dense (vector similarity) search"""
        if self.document_embeddings is None:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)[0]
        
        # Calculate cosine similarities
        similarities = []
        for i, doc_embedding in enumerate(self.document_embeddings):
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append((i, float(similarity)))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _sparse_search(self, query: str, top_k: int = 20) -> List[Tuple[int, float]]:
        """Perform sparse (BM25) search"""
        return self.bm25.search(query, top_k)
    
    def _normalize_scores(self, scores: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
        """Normalize scores to 0-1 range using min-max normalization"""
        if not scores:
            return scores
        
        score_values = [score for _, score in scores]
        min_score = min(score_values)
        max_score = max(score_values)
        
        if max_score == min_score:
            # All scores are the same
            return [(idx, 1.0) for idx, _ in scores]
        
        normalized = []
        for idx, score in scores:
            normalized_score = (score - min_score) / (max_score - min_score)
            normalized.append((idx, normalized_score))
        
        return normalized
    
    def _combine_scores(self, 
                       dense_results: List[Tuple[int, float]],
                       sparse_results: List[Tuple[int, float]]) -> List[RetrievalResult]:
        """Combine dense and sparse scores with hybrid weighting"""
        
        # Normalize scores
        dense_normalized = self._normalize_scores(dense_results)
        sparse_normalized = self._normalize_scores(sparse_results)
        
        # Create score dictionaries
        dense_scores = {idx: score for idx, score in dense_normalized}
        sparse_scores = {idx: score for idx, score in sparse_normalized}
        
        # Get all unique document indices
        all_indices = set(dense_scores.keys()) | set(sparse_scores.keys())
        
        results = []
        for idx in all_indices:
            dense_score = dense_scores.get(idx, 0.0)
            sparse_score = sparse_scores.get(idx, 0.0)
            
            # Calculate hybrid score
            hybrid_score = (self.dense_weight * dense_score + 
                           self.sparse_weight * sparse_score)
            
            # Determine retrieval method
            if idx in dense_scores and idx in sparse_scores:
                method = "hybrid"
            elif idx in dense_scores:
                method = "dense"
            else:
                method = "sparse"
            
            result = RetrievalResult(
                chunk_id=str(idx),
                content=self.documents[idx],
                metadata=self.metadata[idx],
                dense_score=dense_score,
                sparse_score=sparse_score,
                hybrid_score=hybrid_score,
                retrieval_method=method
            )
            results.append(result)
        
        # Sort by hybrid score (descending)
        results.sort(key=lambda x: x.hybrid_score, reverse=True)
        return results
    
    def search_with_fallback(self, 
                           query: str, 
                           top_k: int = 10,
                           dense_top_k: int = 20,
                           sparse_top_k: int = 20) -> List[RetrievalResult]:
        """
        Perform hybrid search with automatic fallback mechanism
        
        Args:
            query: Search query
            top_k: Final number of results to return
            dense_top_k: Number of results from dense search
            sparse_top_k: Number of results from sparse search
            
        Returns:
            List of RetrievalResult objects sorted by hybrid score
        """
        if not self.is_fitted:
            raise ValueError("Hybrid retriever must be fitted before searching")
        
        # Perform dense search
        dense_results = self._dense_search(query, dense_top_k)
        
        # Check if dense search found good results
        best_dense_score = dense_results[0][1] if dense_results else 0.0
        
        if best_dense_score < self.fallback_threshold:
            logger.info(f"Dense search score {best_dense_score:.3f} below threshold {self.fallback_threshold}, using BM25 fallback")
            
            # Use BM25 as primary method
            sparse_results = self._sparse_search(query, top_k)
            
            # Create results primarily from sparse search
            results = []
            for idx, score in sparse_results:
                result = RetrievalResult(
                    chunk_id=str(idx),
                    content=self.documents[idx],
                    metadata=self.metadata[idx],
                    dense_score=0.0,  # Not computed for fallback
                    sparse_score=score,
                    hybrid_score=score,
                    retrieval_method="sparse_fallback"
                )
                results.append(result)
            
            return results[:top_k]
        
        else:
            # Use hybrid approach
            sparse_results = self._sparse_search(query, sparse_top_k)
            combined_results = self._combine_scores(dense_results, sparse_results)
            
            return combined_results[:top_k]
    
    def auto_select_strategy(self, query: str) -> str:
        """
        Automatically select optimal retrieval strategy based on query characteristics
        
        Args:
            query: Search query
            
        Returns:
            Strategy name: "dense", "sparse", or "hybrid"
        """
        query_lower = query.lower()
        
        # Keyword-heavy queries benefit from sparse retrieval
        keyword_indicators = [
            len(re.findall(r'\b\w+\b', query)) > 10,  # Many specific terms
            any(term in query_lower for term in ['name:', 'title:', 'company:', 'date:']),  # Structured queries
            bool(re.search(r'\b\d{4}\b', query)),  # Years/dates
            bool(re.search(r'\$\d+|\d+%', query)),  # Numbers/percentages
        ]
        
        # Semantic queries benefit from dense retrieval
        semantic_indicators = [
            any(term in query_lower for term in ['explain', 'describe', 'what is', 'how does', 'why']),
            len(query.split()) <= 5,  # Short conceptual queries
            any(term in query_lower for term in ['similar', 'related', 'like', 'about']),
        ]
        
        keyword_score = sum(keyword_indicators)
        semantic_score = sum(semantic_indicators)
        
        if keyword_score >= 2:
            return "sparse"
        elif semantic_score >= 2:
            return "dense"
        else:
            return "hybrid"
    
    def search_adaptive(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """
        Perform adaptive search using automatically selected strategy
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of RetrievalResult objects
        """
        strategy = self.auto_select_strategy(query)
        logger.info(f"Using {strategy} retrieval strategy for query: '{query[:50]}...'")
        
        if strategy == "dense":
            dense_results = self._dense_search(query, top_k)
            results = []
            for idx, score in dense_results:
                result = RetrievalResult(
                    chunk_id=str(idx),
                    content=self.documents[idx],
                    metadata=self.metadata[idx],
                    dense_score=score,
                    sparse_score=0.0,
                    hybrid_score=score,
                    retrieval_method="dense_adaptive"
                )
                results.append(result)
            return results
        
        elif strategy == "sparse":
            sparse_results = self._sparse_search(query, top_k)
            results = []
            for idx, score in sparse_results:
                result = RetrievalResult(
                    chunk_id=str(idx),
                    content=self.documents[idx],
                    metadata=self.metadata[idx],
                    dense_score=0.0,
                    sparse_score=score,
                    hybrid_score=score,
                    retrieval_method="sparse_adaptive"
                )
                results.append(result)
            return results
        
        else:  # hybrid
            return self.search_with_fallback(query, top_k)

class RetrievalOptimizer:
    """Optimization utilities for retrieval systems"""
    
    @staticmethod
    def tune_hybrid_weights(queries: List[str],
                           ground_truth: List[List[int]],
                           hybrid_retriever: HybridRetriever,
                           weight_range: Tuple[float, float] = (0.1, 0.9),
                           step: float = 0.1) -> Tuple[float, float]:
        """
        Tune hybrid retrieval weights using grid search
        
        Args:
            queries: List of test queries
            ground_truth: List of relevant document indices for each query
            hybrid_retriever: Fitted hybrid retriever
            weight_range: Range of weights to test
            step: Step size for grid search
            
        Returns:
            Optimal (dense_weight, sparse_weight) tuple
        """
        best_score = 0.0
        best_weights = (0.7, 0.3)
        
        weights = np.arange(weight_range[0], weight_range[1] + step, step)
        
        for dense_weight in weights:
            sparse_weight = 1.0 - dense_weight
            
            # Update retriever weights
            hybrid_retriever.dense_weight = dense_weight
            hybrid_retriever.sparse_weight = sparse_weight
            
            # Evaluate on test queries
            total_score = 0.0
            for query, relevant_docs in zip(queries, ground_truth):
                results = hybrid_retriever.search_with_fallback(query, top_k=10)
                retrieved_indices = [int(r.chunk_id) for r in results]
                
                # Calculate precision@10
                relevant_retrieved = set(retrieved_indices[:10]) & set(relevant_docs)
                precision = len(relevant_retrieved) / min(10, len(retrieved_indices))
                total_score += precision
            
            avg_score = total_score / len(queries)
            
            if avg_score > best_score:
                best_score = avg_score
                best_weights = (dense_weight, sparse_weight)
        
        logger.info(f"Optimal weights: dense={best_weights[0]:.2f}, sparse={best_weights[1]:.2f}, score={best_score:.3f}")
        return best_weights
    
    @staticmethod
    def evaluate_retrieval_performance(queries: List[str],
                                     ground_truth: List[List[int]],
                                     hybrid_retriever: HybridRetriever,
                                     k_values: List[int] = [1, 5, 10]) -> Dict[str, float]:
        """
        Evaluate retrieval performance using standard metrics
        
        Args:
            queries: List of test queries
            ground_truth: List of relevant document indices for each query
            hybrid_retriever: Fitted hybrid retriever
            k_values: Values of k for precision@k and recall@k
            
        Returns:
            Dictionary of evaluation metrics
        """
        metrics = {f'precision@{k}': 0.0 for k in k_values}
        metrics.update({f'recall@{k}': 0.0 for k in k_values})
        metrics['mrr'] = 0.0  # Mean Reciprocal Rank
        
        total_queries = len(queries)
        
        for query, relevant_docs in zip(queries, ground_truth):
            results = hybrid_retriever.search_with_fallback(query, top_k=max(k_values))
            retrieved_indices = [int(r.chunk_id) for r in results]
            
            # Calculate metrics for each k
            for k in k_values:
                retrieved_at_k = set(retrieved_indices[:k])
                relevant_set = set(relevant_docs)
                
                # Precision@k
                if retrieved_at_k:
                    precision_k = len(retrieved_at_k & relevant_set) / len(retrieved_at_k)
                    metrics[f'precision@{k}'] += precision_k
                
                # Recall@k
                if relevant_set:
                    recall_k = len(retrieved_at_k & relevant_set) / len(relevant_set)
                    metrics[f'recall@{k}'] += recall_k
            
            # Mean Reciprocal Rank
            for rank, doc_idx in enumerate(retrieved_indices, 1):
                if doc_idx in relevant_docs:
                    metrics['mrr'] += 1.0 / rank
                    break
        
        # Average metrics
        for key in metrics:
            metrics[key] /= total_queries
        
        return metrics 