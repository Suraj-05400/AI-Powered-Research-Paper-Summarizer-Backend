import logging
from typing import List, Optional, Tuple, TYPE_CHECKING
import os
from app.models import User, ResearchPaper, QASession, QAQuestion, PaperChunk

if TYPE_CHECKING:
    from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class QAService:
    """Service for question-answering on research papers"""
    
    def __init__(self, embedding_service: Optional['EmbeddingService'] = None):
        """Initialize QA service"""
        self.embedding_service = embedding_service
        self.index = None
        self.chunks = []
    
    def setup_qa_system(self, chunks: List[str]):
        """Setup QA system with document chunks"""
        try:
            if self.embedding_service is None:
                from app.services.embedding_service import EmbeddingService
                self.embedding_service = EmbeddingService()
            
            # Create embeddings
            embeddings = self.embedding_service.create_embeddings(chunks)
            
            # Build FAISS index
            self.index = self.embedding_service.build_faiss_index(embeddings)
            self.chunks = chunks
            
            logger.info(f"QA system initialized with {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Error setting up QA system: {e}")
            raise
    
    def answer_question(self, question: str, top_k: int = 5) -> Tuple[str, float, List[int]]:
        """Answer a question about the document"""
        try:
            if self.index is None or not self.chunks or self.embedding_service is None:
                return "QA system not initialized", 0.0, []
            
            # Search for relevant chunks
            relevant_chunks = self.embedding_service.search(
                question, self.index, self.chunks, k=top_k
            )
            
            if not relevant_chunks:
                return "No relevant information found", 0.0, []
            
            # Combine relevant chunks
            context = " ".join([chunk[0] for chunk in relevant_chunks])
            
            # Generate answer using LLM
            answer = self._generate_answer(question, context)
            
            # Calculate confidence score (average similarity of top chunks)
            confidence = sum(chunk[1] for chunk in relevant_chunks) / len(relevant_chunks)
            
            # Get relevant chunk indices
            chunk_indices = [chunk[2] for chunk in relevant_chunks]
            
            return answer, confidence, chunk_indices
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return f"Error: {str(e)}", 0.0, []
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using LLM or simple retrieval"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                # Simple answer generation from context
                return self._simple_answer(question, context)
            
            from langchain_community.llms import OpenAI
            
            llm = OpenAI(temperature=0.5, openai_api_key=api_key)
            
            prompt = f"""Based on the following context, answer the question concisely.

Context: {context}

Question: {question}

Answer:"""
            
            answer = llm.predict(prompt)
            return answer.strip()
        except Exception as e:
            logger.warning(f"Error generating answer with LLM: {e}")
            return self._simple_answer(question, context)
    
    def _simple_answer(self, question: str, context: str) -> str:
        """Generate simple answer from context"""
        from nltk.tokenize import sent_tokenize
        
        sentences = sent_tokenize(context)
        
        # Return first few sentences that might answer the question
        if sentences:
            return " ".join(sentences[:3])
        else:
            return "Could not generate answer from available context."
    
    def get_relevant_chunks(self, question: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Get relevant chunks for a question"""
        if self.index is None or not self.chunks or self.embedding_service is None:
            return []
        
        results = self.embedding_service.search(
            question, self.index, self.chunks, k=top_k
        )
        
        return [(chunk[0], chunk[1]) for chunk in results]
