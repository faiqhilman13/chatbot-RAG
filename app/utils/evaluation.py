"""
RAG Pipeline Evaluation Utilities

This module provides evaluation functions to measure the performance
of the RAG retrieval and generation pipeline.
"""

from typing import List
from difflib import SequenceMatcher
from langchain_core.documents import Document


def recall_at_k(query: str, correct_phrase: str, retriever, k: int = 5) -> bool:
    """
    Check whether the correct_phrase appears in the top k retrieved documents.
    
    This function evaluates retrieval accuracy by checking if the expected
    information is present in the retrieved context.
    
    Args:
        query: The search query to test
        correct_phrase: The phrase that should appear in retrieved documents
        retriever: The retriever object (should have retrieve_context method)
        k: Number of top documents to check (default: 5)
        
    Returns:
        bool: True if correct_phrase is found in any of the top k documents
        
    Example:
        >>> recall = recall_at_k(
        ...     query="What did Faiq do at PwC?",
        ...     correct_phrase="PricewaterhouseCoopers",
        ...     retriever=rag_retriever,
        ...     k=5
        ... )
        >>> print(f"Recall@5: {recall}")
    """
    try:
        # Retrieve top k documents for the query
        retrieved_docs = retriever.retrieve_context(query, k=k)
        
        if not retrieved_docs:
            print(f"[Eval] No documents retrieved for query: '{query}'")
            return False
            
        # Normalize the correct phrase for case-insensitive matching
        correct_phrase_lower = correct_phrase.lower().strip()
        
        # Check if the correct phrase appears in any retrieved document
        for i, doc in enumerate(retrieved_docs):
            if correct_phrase_lower in doc.page_content.lower():
                print(f"[Eval] Found correct phrase in document {i+1}/{len(retrieved_docs)}")
                return True
                
        print(f"[Eval] Correct phrase '{correct_phrase}' not found in top {k} documents")
        return False
        
    except Exception as e:
        print(f"[Eval] Error in recall_at_k: {str(e)}")
        return False


def answer_in_context(answer: str, context_docs: List[Document]) -> float:
    """
    Check how much the generated answer overlaps with the retrieved context.
    
    This function evaluates answer grounding by measuring the similarity
    between the generated answer and the source documents using SequenceMatcher.
    
    Args:
        answer: The generated answer text
        context_docs: List of retrieved documents that were used as context
        
    Returns:
        float: Similarity ratio between 0 and 1 (higher = more grounded in context)
        
    Example:
        >>> docs = [Document(page_content="Faiq worked at PwC as an analyst...")]
        >>> answer = "Faiq was an analyst at PricewaterhouseCoopers"
        >>> grounding_score = answer_in_context(answer, docs)
        >>> print(f"Answer grounding: {grounding_score:.2f}")
    """
    try:
        if not answer or not context_docs:
            print("[Eval] Empty answer or context provided")
            return 0.0
            
        # Normalize answer text
        answer_normalized = answer.lower().strip()
        
        # Combine all context documents into a single text
        combined_context = " ".join([doc.page_content.lower() for doc in context_docs])
        
        if not combined_context:
            print("[Eval] No content in context documents")
            return 0.0
            
        # Use SequenceMatcher to calculate similarity ratio
        matcher = SequenceMatcher(None, answer_normalized, combined_context)
        similarity_ratio = matcher.ratio()
        
        print(f"[Eval] Answer-context similarity: {similarity_ratio:.3f}")
        
        # Also calculate word-level overlap for additional insight
        answer_words = set(answer_normalized.split())
        context_words = set(combined_context.split())
        
        if answer_words:
            word_overlap = len(answer_words.intersection(context_words)) / len(answer_words)
            print(f"[Eval] Word-level overlap: {word_overlap:.3f}")
        
        return similarity_ratio
        
    except Exception as e:
        print(f"[Eval] Error in answer_in_context: {str(e)}")
        return 0.0


def evaluate_rag_pipeline(test_cases: List[dict], retriever, llm_runner) -> dict:
    """
    Comprehensive evaluation of the RAG pipeline using multiple test cases.
    
    Args:
        test_cases: List of test case dictionaries with keys:
                   - 'query': The question to ask
                   - 'expected_phrase': Phrase that should be in retrieved docs
                   - 'expected_answer': (optional) Expected answer for comparison
        retriever: The RAG retriever instance
        llm_runner: The LLM runner instance for generating answers
        
    Returns:
        dict: Evaluation results with recall and grounding scores
        
    Example:
        >>> test_cases = [
        ...     {
        ...         'query': 'What did Faiq do at PwC?',
        ...         'expected_phrase': 'PricewaterhouseCoopers'
        ...     }
        ... ]
        >>> results = evaluate_rag_pipeline(test_cases, rag_retriever, ollama_runner)
    """
    results = {
        'total_cases': len(test_cases),
        'recall_scores': [],
        'grounding_scores': [],
        'detailed_results': []
    }
    
    for i, test_case in enumerate(test_cases):
        print(f"\n[Eval] Running test case {i+1}/{len(test_cases)}")
        print(f"[Eval] Query: {test_case['query']}")
        
        # Test recall
        recall_score = recall_at_k(
            query=test_case['query'],
            correct_phrase=test_case['expected_phrase'],
            retriever=retriever,
            k=5
        )
        
        # Get context and generate answer for grounding test
        context_docs = retriever.retrieve_context(test_case['query'], k=5)
        
        # Generate answer if LLM runner is available
        grounding_score = 0.0
        if context_docs:
            try:
                # Generate answer using the LLM
                context_text = "\n".join([doc.page_content for doc in context_docs])
                answer = llm_runner.get_answer_from_context(test_case['query'], context_text)
                
                # Calculate grounding score
                grounding_score = answer_in_context(answer, context_docs)
                
            except Exception as e:
                print(f"[Eval] Error generating answer: {str(e)}")
        
        # Store results
        case_result = {
            'query': test_case['query'],
            'expected_phrase': test_case['expected_phrase'],
            'recall_at_5': recall_score,
            'grounding_score': grounding_score,
            'num_retrieved_docs': len(context_docs)
        }
        
        results['recall_scores'].append(recall_score)
        results['grounding_scores'].append(grounding_score)
        results['detailed_results'].append(case_result)
    
    # Calculate summary statistics
    results['avg_recall'] = sum(results['recall_scores']) / len(results['recall_scores']) if results['recall_scores'] else 0.0
    results['avg_grounding'] = sum(results['grounding_scores']) / len(results['grounding_scores']) if results['grounding_scores'] else 0.0
    results['recall_rate'] = sum(1 for score in results['recall_scores'] if score) / len(results['recall_scores']) if results['recall_scores'] else 0.0
    
    print(f"\n[Eval] Summary:")
    print(f"[Eval] Recall Rate: {results['recall_rate']:.2%}")
    print(f"[Eval] Average Grounding Score: {results['avg_grounding']:.3f}")
    
    return results 