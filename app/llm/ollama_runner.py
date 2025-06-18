from app.config import LLM_MODEL_NAME, OLLAMA_BASE_URL
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama
import httpx
from typing import Optional, Dict, Any, List

class OllamaRunner:
    def __init__(self):
        """Initialize the Ollama runner"""
        self.model_name = LLM_MODEL_NAME
        self.base_url = OLLAMA_BASE_URL
        self.llm = None
        self.is_available = self._check_availability()
        
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
    
    def get_answer_from_context(self, question: str, context: str) -> str:
        """Get an answer from the LLM using the context"""
        if not self._initialize_llm():
            return self._get_fallback_answer(question, context)
            
        try:
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
            return answer.strip()
        except Exception as e:
            print(f"Error getting answer from LLM: {str(e)}")
            return self._get_fallback_answer(question, context)
    
    def _get_fallback_answer(self, question: str, context: str) -> str:
        """Provide a fallback answer when LLM is unavailable"""
        if not context:
            return "I don't have any relevant information to answer your question. Please try uploading more documents."
            
        # Simple fallback that just returns the context
        return f"I found the following information that might help answer your question:\n\n{context[:1000]}...\n\n(Note: Ollama LLM service is not available, so I'm showing you the raw retrieved context instead of a generated answer.)"

# Create a singleton instance
ollama_runner = OllamaRunner() 