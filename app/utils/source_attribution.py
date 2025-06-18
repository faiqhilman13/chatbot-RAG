import re
from typing import List, Dict, Any, Tuple, Optional
from langchain.schema import Document
from dataclasses import dataclass
from collections import defaultdict, Counter

@dataclass
class SourceAnchor:
    """Represents an anchored source with metadata."""
    document_id: str
    source_file: str
    page_number: Optional[int]
    title: Optional[str]
    chunk_id: str
    content_snippet: str
    confidence_score: float

@dataclass
class CitationValidation:
    """Results of citation validation analysis."""
    valid_citations: List[SourceAnchor]
    invalid_citations: List[str]
    missing_citations: List[SourceAnchor]
    citation_accuracy: float
    recommendations: List[str]

class SourceAttributionManager:
    """Manages source attribution, citation validation, and cross-document references."""
    
    def __init__(self):
        """Initialize the source attribution manager."""
        self.source_anchors: Dict[str, SourceAnchor] = {}
        
    def create_anchored_chunks(self, docs: List[Document]) -> List[Document]:
        """Format chunks with explicit source metadata anchoring."""
        anchored_docs = []
        
        for i, doc in enumerate(docs):
            # Extract metadata
            source_file = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "N/A")
            title = doc.metadata.get("title", "Unknown")
            doc_id = doc.metadata.get("doc_id", f"doc_{i}")
            
            # Create unique chunk identifier
            chunk_id = f"{doc_id}_chunk_{i}"
            
            # Create source anchor
            source_anchor = SourceAnchor(
                document_id=doc_id,
                source_file=source_file,
                page_number=page if isinstance(page, int) else None,
                title=title,
                chunk_id=chunk_id,
                content_snippet=doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content,
                confidence_score=1.0  # Default confidence
            )
            
            # Store anchor for later reference
            self.source_anchors[chunk_id] = source_anchor
            
            # Format content with explicit source metadata
            anchored_content = self._format_chunk_with_anchor(doc.page_content, source_anchor)
            
            # Create new document with anchored content
            anchored_doc = Document(
                page_content=anchored_content,
                metadata={
                    **doc.metadata,
                    "chunk_id": chunk_id,
                    "source_anchor": source_anchor,
                    "formatted_with_anchor": True
                }
            )
            
            anchored_docs.append(anchored_doc)
        
        print(f"[SourceAttribution] Created {len(anchored_docs)} anchored chunks")
        return anchored_docs
    
    def _format_chunk_with_anchor(self, content: str, anchor: SourceAnchor) -> str:
        """Format chunk content with explicit source anchor."""
        source_info = f"[SOURCE: {anchor.source_file}"
        
        if anchor.page_number:
            source_info += f" | PAGE: {anchor.page_number}"
        
        if anchor.title and anchor.title != "Unknown":
            source_info += f" | TITLE: {anchor.title}"
        
        source_info += f" | ID: {anchor.chunk_id}]"
        
        # Add source anchor at the beginning and end for clarity
        formatted_content = f"{source_info}\n\n{content}\n\n{source_info}"
        
        return formatted_content
    
    def validate_answer_citations(self, answer: str, source_docs: List[Document]) -> CitationValidation:
        """Validate that generated answers properly cite correct source documents."""
        
        # Extract mentioned sources from the answer
        mentioned_sources = self._extract_mentioned_sources(answer)
        
        # Get available sources from documents
        available_sources = self._get_available_sources(source_docs)
        
        # Validate citations
        valid_citations = []
        invalid_citations = []
        missing_citations = []
        
        for mentioned in mentioned_sources:
            # Check if mentioned source exists in available sources
            found_match = False
            for available in available_sources:
                if self._sources_match(mentioned, available):
                    valid_citations.append(available)
                    found_match = True
                    break
            
            if not found_match:
                invalid_citations.append(mentioned)
        
        # Check for missing citations (sources that should be cited but aren't)
        for available in available_sources:
            if not any(self._sources_match(mentioned, available) for mentioned in mentioned_sources):
                # Check if content from this source appears to be used in the answer
                if self._content_appears_used(answer, available, source_docs):
                    missing_citations.append(available)
        
        # Calculate citation accuracy
        total_sources = len(available_sources)
        accurate_citations = len(valid_citations)
        citation_accuracy = accurate_citations / total_sources if total_sources > 0 else 0.0
        
        # Generate recommendations
        recommendations = self._generate_citation_recommendations(
            valid_citations, invalid_citations, missing_citations
        )
        
        validation = CitationValidation(
            valid_citations=valid_citations,
            invalid_citations=invalid_citations,
            missing_citations=missing_citations,
            citation_accuracy=citation_accuracy,
            recommendations=recommendations
        )
        
        print(f"[SourceAttribution] Citation validation: {citation_accuracy:.2f} accuracy, {len(valid_citations)} valid, {len(invalid_citations)} invalid, {len(missing_citations)} missing")
        
        return validation
    
    def _extract_mentioned_sources(self, answer: str) -> List[str]:
        """Extract source mentions from the generated answer."""
        mentioned_sources = []
        
        # Pattern to match source citations in the answer
        source_patterns = [
            r'according to ([^,\n]+)',
            r'from ([^,\n]+)',
            r'in ([^,\n]+)',
            r'source: ([^,\n]+)',
            r'\[SOURCE: ([^\]]+)\]',
            r'based on ([^,\n]+)',
            r'as stated in ([^,\n]+)'
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, answer, re.IGNORECASE)
            mentioned_sources.extend(matches)
        
        # Clean up extracted sources
        mentioned_sources = [source.strip().strip('"\'') for source in mentioned_sources]
        
        return mentioned_sources
    
    def _get_available_sources(self, docs: List[Document]) -> List[SourceAnchor]:
        """Get list of available source anchors from documents."""
        available_sources = []
        
        for doc in docs:
            if "source_anchor" in doc.metadata:
                available_sources.append(doc.metadata["source_anchor"])
            else:
                # Create anchor from metadata if not already anchored
                source_file = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", None)
                title = doc.metadata.get("title", "Unknown")
                doc_id = doc.metadata.get("doc_id", "unknown")
                
                anchor = SourceAnchor(
                    document_id=doc_id,
                    source_file=source_file,
                    page_number=page if isinstance(page, int) else None,
                    title=title,
                    chunk_id=f"{doc_id}_inferred",
                    content_snippet=doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content,
                    confidence_score=0.8
                )
                available_sources.append(anchor)
        
        return available_sources
    
    def _sources_match(self, mentioned: str, available: SourceAnchor) -> bool:
        """Check if a mentioned source matches an available source anchor."""
        mentioned_lower = mentioned.lower()
        
        # Check against various source identifiers
        checks = [
            available.source_file.lower() in mentioned_lower,
            mentioned_lower in available.source_file.lower(),
            available.title and (available.title.lower() in mentioned_lower or mentioned_lower in available.title.lower()),
            available.chunk_id.lower() in mentioned_lower
        ]
        
        return any(checks)
    
    def _content_appears_used(self, answer: str, source_anchor: SourceAnchor, docs: List[Document]) -> bool:
        """Check if content from a source appears to be used in the answer."""
        # Find the document corresponding to this source anchor
        source_doc = None
        for doc in docs:
            if (doc.metadata.get("source") == source_anchor.source_file and 
                doc.metadata.get("page") == source_anchor.page_number):
                source_doc = doc
                break
        
        if not source_doc:
            return False
        
        # Extract key phrases from the source document
        source_words = set(re.findall(r'\b\w{4,}\b', source_doc.page_content.lower()))
        answer_words = set(re.findall(r'\b\w{4,}\b', answer.lower()))
        
        # Calculate word overlap
        overlap = len(source_words.intersection(answer_words))
        overlap_ratio = overlap / len(source_words) if source_words else 0
        
        # Consider content used if there's significant word overlap
        return overlap_ratio > 0.15
    
    def _generate_citation_recommendations(self, valid: List[SourceAnchor], 
                                         invalid: List[str], 
                                         missing: List[SourceAnchor]) -> List[str]:
        """Generate recommendations for improving citations."""
        recommendations = []
        
        if invalid:
            recommendations.append(f"Remove {len(invalid)} invalid citation(s): {', '.join(invalid[:3])}")
        
        if missing:
            missing_sources = [f"{anchor.source_file} (page {anchor.page_number})" for anchor in missing[:3]]
            recommendations.append(f"Add missing citation(s) for: {', '.join(missing_sources)}")
        
        if len(valid) == 0:
            recommendations.append("Add proper source citations to support the answer")
        
        if len(valid) > 0 and len(missing) == 0 and len(invalid) == 0:
            recommendations.append("Citations are accurate and complete")
        
        return recommendations
    
    def detect_cross_document_references(self, docs: List[Document]) -> Dict[str, List[str]]:
        """Detect cases where answers should reference multiple documents."""
        
        # Group documents by source
        docs_by_source = defaultdict(list)
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            docs_by_source[source].append(doc)
        
        cross_references = {}
        
        # If we have multiple sources, analyze for cross-references
        if len(docs_by_source) > 1:
            sources = list(docs_by_source.keys())
            
            for i, source1 in enumerate(sources):
                for j, source2 in enumerate(sources[i+1:], i+1):
                    # Find common themes/entities between sources
                    common_themes = self._find_common_themes(
                        docs_by_source[source1], 
                        docs_by_source[source2]
                    )
                    
                    if common_themes:
                        ref_key = f"{source1} <-> {source2}"
                        cross_references[ref_key] = common_themes
        
        if cross_references:
            print(f"[SourceAttribution] Detected {len(cross_references)} cross-document references")
        
        return cross_references
    
    def _find_common_themes(self, docs1: List[Document], docs2: List[Document]) -> List[str]:
        """Find common themes/entities between two sets of documents."""
        
        # Extract key terms from both document sets
        terms1 = set()
        terms2 = set()
        
        for doc in docs1:
            words = re.findall(r'\b[A-Z][a-z]+\b|\b\w{5,}\b', doc.page_content)
            terms1.update(word.lower() for word in words)
        
        for doc in docs2:
            words = re.findall(r'\b[A-Z][a-z]+\b|\b\w{5,}\b', doc.page_content)
            terms2.update(word.lower() for word in words)
        
        # Find common significant terms
        common_terms = terms1.intersection(terms2)
        
        # Filter for meaningful terms (not common words)
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'her', 'way', 'may', 'said', 'each', 'which', 'she', 'this', 'that', 'with', 'have', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were', 'will'}
        
        meaningful_terms = [term for term in common_terms 
                          if len(term) > 3 and term not in stopwords]
        
        # Return top common themes
        return meaningful_terms[:10]
    
    def generate_source_aware_prompt(self, question: str, anchored_docs: List[Document]) -> str:
        """Generate a prompt that includes source awareness instructions."""
        
        # Extract source information
        sources_info = []
        for doc in anchored_docs:
            anchor = doc.metadata.get("source_anchor")
            if anchor:
                source_info = f"- {anchor.source_file}"
                if anchor.page_number:
                    source_info += f" (Page {anchor.page_number})"
                if anchor.title and anchor.title != "Unknown":
                    source_info += f" - {anchor.title}"
                sources_info.append(source_info)
        
        # Detect cross-document references
        cross_refs = self.detect_cross_document_references(anchored_docs)
        
        prompt = f"""You are an AI assistant answering questions based on provided context with STRICT source attribution requirements.

# CRITICAL SOURCE ATTRIBUTION RULES

1. **MANDATORY CITATION**: Every factual claim MUST include a source citation in the format [SOURCE: filename | PAGE: X]
2. **SOURCE VALIDATION**: Only use information that is explicitly present in the provided sources
3. **NO MIXING**: Do not mix information from different sources unless explicitly comparing them
4. **CROSS-REFERENCE AWARENESS**: When information spans multiple sources, cite each relevant source

# AVAILABLE SOURCES
{chr(10).join(sources_info)}

# CROSS-DOCUMENT REFERENCES DETECTED
{self._format_cross_references(cross_refs)}

# CONTEXT WITH SOURCE ANCHORS
{chr(10).join([doc.page_content for doc in anchored_docs])}

# QUESTION
{question}

# INSTRUCTIONS FOR ANSWER
- Begin each factual statement with the relevant source citation
- If comparing information from multiple sources, cite each source separately
- If information is contradictory between sources, acknowledge this explicitly
- If you cannot find relevant information in the sources, state this clearly
- End your answer with a summary of all sources consulted

# ANSWER"""

        return prompt
    
    def _format_cross_references(self, cross_refs: Dict[str, List[str]]) -> str:
        """Format cross-references for inclusion in prompts."""
        if not cross_refs:
            return "None detected - sources appear to cover different topics"
        
        formatted = []
        for ref_pair, themes in cross_refs.items():
            themes_str = ", ".join(themes[:5])
            formatted.append(f"- {ref_pair}: Common themes include {themes_str}")
        
        return "\n".join(formatted)

# Create singleton instance
source_attribution_manager = SourceAttributionManager() 