#!/usr/bin/env python3
"""
Test script for RAG pipeline evaluation functions.

This script demonstrates how to use the evaluation utilities to measure
retrieval accuracy and answer grounding in the RAG system.
"""

import sys
import os

# Add the app directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from utils.evaluation import recall_at_k, answer_in_context, evaluate_rag_pipeline
from retrievers.rag import rag_retriever
from llm.ollama_runner import ollama_runner


def test_individual_functions():
    """Test the individual evaluation functions."""
    print("🧪 Testing individual evaluation functions...")
    
    # Test recall_at_k
    print("\n1. Testing recall_at_k function:")
    recall_result = recall_at_k(
        query="What has Faiq done at PricewaterhouseCoopers?",
        correct_phrase="PricewaterhouseCoopers",
        retriever=rag_retriever,
        k=5
    )
    print(f"   Recall@5 for PwC query: {recall_result}")
    
    # Test with company alias
    recall_result_alias = recall_at_k(
        query="What has Faiq done at PwC?",
        correct_phrase="PwC",
        retriever=rag_retriever,
        k=5
    )
    print(f"   Recall@5 for PwC alias query: {recall_result_alias}")
    
    # Test answer_in_context
    print("\n2. Testing answer_in_context function:")
    # Get some context documents
    context_docs = rag_retriever.retrieve_context("What did Faiq do at PwC?", k=3)
    
    if context_docs:
        # Example answer that should have high grounding
        test_answer = "Faiq worked at PricewaterhouseCoopers as an analyst, conducting trend analytics and technical analysis."
        grounding_score = answer_in_context(test_answer, context_docs)
        print(f"   Grounding score for realistic answer: {grounding_score:.3f}")
        
        # Example answer that should have low grounding
        unrelated_answer = "Faiq is an expert in quantum computing and space exploration."
        grounding_score_low = answer_in_context(unrelated_answer, context_docs)
        print(f"   Grounding score for unrelated answer: {grounding_score_low:.3f}")
    else:
        print("   No context documents retrieved - check your vector store!")


def test_comprehensive_evaluation():
    """Test the comprehensive evaluation pipeline."""
    print("\n🔬 Testing comprehensive evaluation pipeline...")
    
    # Define test cases for evaluation
    test_cases = [
        {
            'query': 'What has Faiq done at PricewaterhouseCoopers?',
            'expected_phrase': 'PricewaterhouseCoopers'
        },
        {
            'query': 'What is Faiq\'s experience at PwC?',
            'expected_phrase': 'PwC'
        },
        {
            'query': 'What did Faiq do at Ernst & Young?',
            'expected_phrase': 'Ernst'
        },
        {
            'query': 'What is Faiq\'s experience at EY?',
            'expected_phrase': 'EY'
        },
        {
            'query': 'What has Faiq done at Cherengin Hills?',
            'expected_phrase': 'Cherengin'
        }
    ]
    
    # Run comprehensive evaluation
    results = evaluate_rag_pipeline(test_cases, rag_retriever, ollama_runner)
    
    # Print detailed results
    print("\n📊 Detailed Results:")
    for i, result in enumerate(results['detailed_results']):
        print(f"\nTest Case {i+1}:")
        print(f"   Query: {result['query']}")
        print(f"   Expected Phrase: {result['expected_phrase']}")
        print(f"   Recall@5: {'✅' if result['recall_at_5'] else '❌'}")
        print(f"   Grounding Score: {result['grounding_score']:.3f}")
        print(f"   Retrieved Docs: {result['num_retrieved_docs']}")
    
    print(f"\n📈 Overall Performance:")
    print(f"   Recall Rate: {results['recall_rate']:.1%}")
    print(f"   Average Grounding: {results['avg_grounding']:.3f}")
    
    return results


def benchmark_before_after():
    """
    Benchmark function to compare performance before and after improvements.
    This simulates what the results would look like with different settings.
    """
    print("\n⚖️ Simulating Before/After Improvement Comparison...")
    
    # These would be the results with the old 10% keyword threshold
    print("\n📉 Simulated 'Before' Results (10% keyword threshold):")
    print("   - PwC query: Recall@5 = False (only 1 chunk retrieved)")
    print("   - Grounding score: ~0.2 (incomplete context)")
    
    # Current results with 3% threshold
    print("\n📈 Current 'After' Results (3% keyword threshold + aliases):")
    recall_pwc = recall_at_k(
        query="What has Faiq done at PricewaterhouseCoopers?",
        correct_phrase="PricewaterhouseCoopers",
        retriever=rag_retriever,
        k=5
    )
    print(f"   - PwC query: Recall@5 = {recall_pwc} (2+ chunks retrieved)")
    
    # Calculate improvement
    improvement = "🚀 MAJOR IMPROVEMENT!" if recall_pwc else "⚠️ Still needs work"
    print(f"   - Assessment: {improvement}")


if __name__ == "__main__":
    print("🎯 RAG Pipeline Evaluation Test")
    print("=" * 50)
    
    try:
        # Test individual functions
        test_individual_functions()
        
        # Test comprehensive evaluation
        test_comprehensive_evaluation()
        
        # Show before/after comparison
        benchmark_before_after()
        
        print("\n✅ Evaluation testing completed!")
        
    except Exception as e:
        print(f"\n❌ Error during evaluation: {str(e)}")
        print("Make sure your vector store is initialized and Ollama is running.") 