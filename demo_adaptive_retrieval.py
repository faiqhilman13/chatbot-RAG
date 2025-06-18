#!/usr/bin/env python3
"""
Demonstration of Adaptive Retrieval Intelligence and Enhanced Source Attribution

This script demonstrates the new features implemented:
1. Dynamic Retrieval K based on query type and complexity
2. Query Complexity Classification  
3. Adaptive Chunk Size Selection
4. Chunk Anchoring with Source Metadata
5. Source Citation Validation
6. Cross-Document Reference Detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.query_analyzer import query_analyzer, QueryType, QueryComplexity
from app.utils.source_attribution import source_attribution_manager
from langchain.schema import Document

def demonstrate_adaptive_retrieval():
    """Demonstrate the adaptive retrieval intelligence features."""
    
    print("🧠 ADAPTIVE RETRIEVAL INTELLIGENCE DEMONSTRATION")
    print("=" * 60)
    
    # Test queries of different types and complexities
    test_queries = [
        "Who is Faiq Hilman?",  # Simple entity query
        "What is machine learning?",  # Definition query
        "Summarize his work experience",  # Summary query
        "Why did he choose to work at PwC and how did this decision impact his career?",  # Complex reasoning
        "Compare and analyze the different roles he had across multiple companies, evaluate their strategic importance, and synthesize insights about his career progression pattern",  # Very complex
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 40)
        
        # Analyze the query
        analysis = query_analyzer.analyze_query(query)
        
        print(f"🎯 Query Type: {analysis.query_type.value.upper()}")
        print(f"🔥 Complexity: {analysis.complexity.value.upper()}")
        print(f"📊 Optimal K: {analysis.optimal_k} documents")
        print(f"📏 Recommended Chunk Size: {analysis.chunk_size} tokens")
        print(f"🔗 Recommended Overlap: {analysis.chunk_overlap} tokens")
        print(f"🎪 Confidence: {analysis.confidence:.2f}")
        
        if analysis.detected_entities:
            print(f"👤 Entities: {', '.join(analysis.detected_entities)}")
        
        if analysis.keywords:
            print(f"🔍 Keywords: {', '.join(analysis.keywords[:5])}")  # Show first 5

def demonstrate_source_attribution():
    """Demonstrate the enhanced source attribution features."""
    
    print("\n\n🧾 ENHANCED SOURCE ATTRIBUTION DEMONSTRATION")
    print("=" * 60)
    
    # Create sample documents
    sample_docs = [
        Document(
            page_content="Faiq Hilman worked as a Senior Consultant at PricewaterhouseCoopers (PwC) from January 2020 to December 2022. He led data analytics projects for Fortune 500 clients.",
            metadata={
                "source": "faiq_cv.pdf",
                "page": 1,
                "title": "Faiq Hilman CV",
                "doc_id": "cv_001"
            }
        ),
        Document(
            page_content="During his tenure at PwC, Faiq specialized in machine learning implementations and helped clients reduce operational costs by an average of 15%.",
            metadata={
                "source": "faiq_cv.pdf", 
                "page": 2,
                "title": "Faiq Hilman CV",
                "doc_id": "cv_001"
            }
        ),
        Document(
            page_content="Tesla reported record revenue of $96.8 billion in fiscal year 2024, representing a 15% increase from the previous year.",
            metadata={
                "source": "tesla_fy24.pdf",
                "page": 5,
                "title": "Tesla Annual Report 2024",
                "doc_id": "tesla_001"
            }
        )
    ]
    
    print(f"\n📚 Original Documents: {len(sample_docs)}")
    for i, doc in enumerate(sample_docs, 1):
        print(f"   {i}. {doc.metadata['source']} (Page {doc.metadata['page']})")
    
    # Create anchored chunks
    print(f"\n🔗 Creating Anchored Chunks...")
    anchored_docs = source_attribution_manager.create_anchored_chunks(sample_docs)
    
    print(f"\n📋 Anchored Content Example:")
    print("=" * 40)
    print(anchored_docs[0].page_content[:200] + "...")
    
    # Detect cross-document references
    print(f"\n🔍 Cross-Document Reference Detection:")
    cross_refs = source_attribution_manager.detect_cross_document_references(anchored_docs)
    
    if cross_refs:
        for ref_pair, themes in cross_refs.items():
            print(f"   📎 {ref_pair}: {', '.join(themes[:3])}")
    else:
        print("   ✅ No cross-references detected (sources cover different topics)")
    
    # Test citation validation
    print(f"\n📝 Citation Validation Example:")
    sample_answer = "[SOURCE: faiq_cv.pdf | PAGE: 1] Faiq Hilman worked as a Senior Consultant at PwC from 2020 to 2022."
    validation = source_attribution_manager.validate_answer_citations(sample_answer, anchored_docs)
    
    print(f"   ✅ Valid Citations: {len(validation.valid_citations)}")
    print(f"   ❌ Invalid Citations: {len(validation.invalid_citations)}")
    print(f"   ⚠️  Missing Citations: {len(validation.missing_citations)}")
    print(f"   📊 Citation Accuracy: {validation.citation_accuracy:.2f}")
    
    if validation.recommendations:
        print(f"   💡 Recommendations: {'; '.join(validation.recommendations)}")
    
    # Generate source-aware prompt
    print(f"\n🎯 Source-Aware Prompt Generation:")
    question = "What did Faiq do at PwC?"
    prompt = source_attribution_manager.generate_source_aware_prompt(question, anchored_docs)
    
    print("=" * 40)
    print(prompt[:400] + "...")
    print("=" * 40)

def demonstrate_integrated_features():
    """Demonstrate how adaptive retrieval and source attribution work together."""
    
    print("\n\n🚀 INTEGRATED ADAPTIVE RETRIEVAL DEMONSTRATION")
    print("=" * 60)
    
    queries = [
        ("Who is Faiq?", "Simple entity query"),
        ("Summarize Faiq's consulting experience", "Summary query"),
        ("Analyze the strategic impact of Faiq's work at PwC", "Complex reasoning query")
    ]
    
    for query, description in queries:
        print(f"\n🎯 {description}: '{query}'")
        print("-" * 50)
        
        # Step 1: Analyze query
        analysis = query_analyzer.analyze_query(query)
        print(f"1️⃣  Query Analysis: {analysis.query_type.value} | {analysis.complexity.value} | K={analysis.optimal_k}")
        
        # Step 2: Simulate retrieval (in real system, this would query the vector store)
        print(f"2️⃣  Simulated Retrieval: Would retrieve {analysis.optimal_k} most relevant chunks")
        
        # Step 3: Source attribution
        print(f"3️⃣  Source Attribution: Would add explicit source anchors to all chunks")
        
        # Step 4: Enhanced prompting
        print(f"4️⃣  Enhanced Prompting: Would use source-aware prompt with citation requirements")
        
        # Step 5: Citation validation  
        print(f"5️⃣  Citation Validation: Would validate answer citations and provide recommendations")

def main():
    """Main demonstration function."""
    
    print("🎪 ADAPTIVE RETRIEVAL & SOURCE ATTRIBUTION DEMO")
    print("=" * 70)
    print("\nThis demonstration shows the new RAG features:")
    print("✅ Dynamic Retrieval K based on query analysis")
    print("✅ Query complexity classification")
    print("✅ Adaptive chunk size recommendations")
    print("✅ Chunk anchoring with source metadata")
    print("✅ Source citation validation")
    print("✅ Cross-document reference detection")
    print("✅ Source-aware prompt generation")
    
    try:
        demonstrate_adaptive_retrieval()
        demonstrate_source_attribution()
        demonstrate_integrated_features()
        
        print("\n\n🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📖 The adaptive retrieval system is now ready to:")
        print("   🔍 Automatically optimize retrieval parameters based on query characteristics")
        print("   📚 Provide enhanced source attribution with explicit citations")
        print("   🔗 Detect and handle cross-document references")
        print("   ✅ Validate citation accuracy in generated answers")
        print("   🎯 Generate source-aware prompts for better LLM responses")
        
        print("\n🚀 These features significantly improve:")
        print("   📈 Retrieval accuracy and relevance")
        print("   🔒 Source transparency and traceability")
        print("   🎯 Answer quality and factual grounding")
        print("   🛡️  Reduced hallucination and source mixing")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        print("💡 This might be due to missing dependencies (spaCy model)")
        print("   Run: python -m spacy download en_core_web_sm")

if __name__ == "__main__":
    main() 