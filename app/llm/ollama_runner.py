from app.config import LLM_MODEL_NAME, OLLAMA_BASE_URL
from app.utils.source_attribution import source_attribution_manager
from app.utils.answer_evaluator import AnswerEvaluator
from app.utils.performance_monitor import get_performance_monitor, QueryMetrics
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama
import httpx
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from langchain.schema import Document

class OllamaRunner:
    def __init__(self):
        """Initialize the Ollama runner"""
        self.model_name = LLM_MODEL_NAME
        self.base_url = OLLAMA_BASE_URL
        self.llm = None
        self.is_available = self._check_availability()
        self.answer_evaluator = AnswerEvaluator(ollama_runner=self)
        self.performance_monitor = get_performance_monitor()
        self._last_retrieval_time = 0.0
        
    def _check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(f"{self.base_url}/api/version")
                if response.status_code == 200:
                    print(f"Ollama is available: {response.json()}")
                    return True
                else:
                    print(f"Ollama returned error status: {response.status_code}")
        except Exception as e:
            print(f"Ollama is not available: {str(e)}")
        return False
    
    def _initialize_llm(self) -> bool:
        """Initialize the LLM"""
        if self.llm:
            return True
            
        if not self.is_available:
            print("Ollama is not available")
            return False
            
        try:
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.7
            )
            return True
        except Exception as e:
            print(f"Error initializing LLM: {str(e)}")
            return False
    
    def get_answer_from_context(self, question: str, context: str, source_docs: Optional[List[Document]] = None) -> str:
        """Get an answer from the LLM using the context with enhanced source attribution and quality monitoring"""
        
        # Start timing for performance monitoring
        start_time = time.time()
        llm_start_time = None
        query_id = str(uuid.uuid4())[:8]
        
        if not self._initialize_llm():
            # Record failed query metrics
            self._record_query_metrics(
                query_id, question, "", context, source_docs,
                start_time, 0.0, self._last_retrieval_time, 0.0, error_occurred=True,
                error_message="LLM not available"
            )
            return self._get_fallback_answer(question, context)
            
        try:
            llm_start_time = time.time()
            answer = ""
            
            # Use source-aware prompt if source documents are provided and have anchors
            if source_docs and any(doc.metadata.get("formatted_with_anchor") for doc in source_docs):
                print("[LLM] Using source-aware prompt with explicit source attribution")
                # Generate source-aware prompt using source attribution manager
                prompt_text = source_attribution_manager.generate_source_aware_prompt(question, source_docs)
                
                # Create a simple prompt template for the source-aware prompt
                prompt = ChatPromptTemplate.from_template("{prompt_text}")
                chain = LLMChain(llm=self.llm, prompt=prompt)
                answer = chain.run({"prompt_text": prompt_text})
                
                # Validate citations in the generated answer
                citation_validation = source_attribution_manager.validate_answer_citations(answer, source_docs)
                
                if citation_validation.citation_accuracy < 0.5:
                    print(f"[LLM] Low citation accuracy ({citation_validation.citation_accuracy:.2f}), adding recommendations")
                    if citation_validation.recommendations:
                        answer += f"\n\n[CITATION RECOMMENDATIONS: {'; '.join(citation_validation.recommendations)}]"
                
            else:
                # Fall back to standard prompt
                print("[LLM] Using standard prompt (no source anchors available)")
                template = """
                You are an AI assistant answering questions based on the provided context.
                
                # INSTRUCTIONS
                1. Answer the question using ONLY the provided context.
                2. If the answer cannot be found in the context, respond with "I don't have enough information to answer that question."
                3. IMPORTANT: Evaluate the relevance of each source before using it. Discard any sources that are not directly relevant to the question.
                4. Focus on quality over quantity - use only the most relevant sources.
                5. If sources contradict each other, explain the discrepancy.
                6. If the context contains irrelevant documents (like financial statements when asked about a person's experience), IGNORE those completely.
                
                # SOURCE VALIDATION
                Before answering, analyze each source for relevance to the question:
                - For questions about people (experience, education, skills), only use CV/resume documents
                - For questions about companies or financial information, only use relevant reports
                - For technical questions, only use technical documentation
                - Discard any source that doesn't directly relate to the question topic
                
                # CONTEXT
                {context}
                
                # QUESTION
                {question}
                
                # ANSWER
                """
                
                prompt = ChatPromptTemplate.from_template(template)
                chain = LLMChain(llm=self.llm, prompt=prompt)
                answer = chain.run({"context": context, "question": question})
            
            llm_end_time = time.time()
            llm_time = llm_end_time - llm_start_time
            
            # 🧪 ADVANCED ANSWER EVALUATION & QUALITY CONTROL
            # Evaluate answer quality using LLM-as-a-Judge
            context_chunks = [doc.page_content for doc in source_docs] if source_docs else [context]
            processing_time = time.time() - start_time
            
            # Use a separate evaluation instance to avoid recursion
            try:
                quality_metrics = self.answer_evaluator.evaluate_answer_quality(
                    query=question,
                    answer=answer.strip(),
                    context=context_chunks,
                    processing_time=processing_time
                )
                print(f"[AnswerEvaluation] Quality Score: {quality_metrics.overall_score:.2f}/5.0, Confidence: {quality_metrics.confidence_score:.2f}")
                
                # Add quality indicator to answer if score is low
                if quality_metrics.overall_score < 2.5:
                    answer += f"\n\n[QUALITY NOTICE: This answer has a low quality score of {quality_metrics.overall_score:.1f}/5.0. Please verify the information.]"
                    
            except Exception as eval_error:
                print(f"[AnswerEvaluation] Error during evaluation: {eval_error}")
                # Create default metrics for monitoring
                quality_metrics = None
            
            # Record performance metrics
            self._record_query_metrics(
                query_id, question, answer.strip(), context, source_docs,
                start_time, llm_time, self._last_retrieval_time, processing_time,
                quality_metrics=quality_metrics
            )
            
            return answer.strip()
            
        except Exception as e:
            print(f"Error getting answer from LLM: {str(e)}")
            
            # Record error metrics
            self._record_query_metrics(
                query_id, question, "", context, source_docs,
                start_time, 0.0, self._last_retrieval_time, time.time() - start_time,
                error_occurred=True, error_message=str(e)
            )
            
            return self._get_fallback_answer(question, context)
    
    def _record_query_metrics(self, query_id: str, question: str, answer: str, 
                             context: str, source_docs: Optional[List[Document]],
                             start_time: float, llm_time: float, retrieval_time: float, 
                             processing_time: float, quality_metrics=None,
                             error_occurred: bool = False, error_message: str = None):
        """Record detailed query metrics for performance monitoring"""
        try:
            metrics = QueryMetrics(
                query_id=query_id,
                query_text=question,
                timestamp=datetime.now().isoformat(),
                processing_time=processing_time,
                retrieval_time=retrieval_time,
                llm_time=llm_time,
                total_chunks_retrieved=len(source_docs) if source_docs else 1,
                final_chunks_used=len(source_docs) if source_docs else 1,
                retrieval_method=source_docs[0].metadata.get('retrieval_method', 'standard') if source_docs else 'standard',
                answer_quality_score=quality_metrics.overall_score if quality_metrics else 3.0,
                confidence_score=quality_metrics.confidence_score if quality_metrics else 0.5,
                error_occurred=error_occurred,
                error_message=error_message
            )
            
            self.performance_monitor.record_query_metrics(metrics)
            
        except Exception as e:
            print(f"Error recording query metrics: {e}")
    
    def _get_fallback_answer(self, question: str, context: str) -> str:
        """Provide a fallback answer when LLM is unavailable"""
        if not context:
            return "I don't have any relevant information to answer your question. Please try uploading more documents."
            
        # Simple fallback that just returns the context
        return f"I found the following information that might help answer your question:\n\n{context[:1000]}...\n\n(Note: Ollama LLM service is not available, so I'm showing you the raw retrieved context instead of a generated answer.)"

# Create a singleton instance
ollama_runner = OllamaRunner() 