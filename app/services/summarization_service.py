import logging
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_classic.chains.summarize import load_summarize_chain
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class SummarizationService:
    """Service for summarizing research papers using LangChain"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """Initialize summarization service"""
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Using fallback summarization.")
        
        # Initialize text splitter lazily
        self._text_splitter = None
    
    @property
    def text_splitter(self):
        """Lazy initialization of text splitter"""
        if self._text_splitter is None:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            self._text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=4000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
        return self._text_splitter
    
    def summarize(self, text: str, max_length: int = 500) -> str:
        """Summarize text using LangChain"""
        try:
            if self.api_key:
                return self._summarize_with_llm(text, max_length)
            else:
                return self._fallback_summarize(text, max_length)
        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            return self._fallback_summarize(text, max_length)
    
    def _summarize_with_llm(self, text: str, max_length: int) -> str:
        """Summarize using LangChain with OpenAI"""
        try:
            from langchain_community.llms import OpenAI
            from langchain_core.documents import Document
            from langchain_classic.chains.summarize import load_summarize_chain
            
            llm = OpenAI(temperature=0, model_name=self.model_name, openai_api_key=self.api_key)
            
            # Split text into documents
            docs = [Document(page_content=text)]
            
            # Load summarization chain
            chain = load_summarize_chain(llm, chain_type="stuff")
            
            # Generate summary
            summary = chain.run(docs)
            logger.info(f"Summarization completed")
            
            # Truncate to max_length if needed
            if len(summary.split()) > max_length:
                summary = ' '.join(summary.split()[:max_length])
            
            return summary
        except Exception as e:
            logger.error(f"Error in LLM summarization: {e}")
            return self._fallback_summarize(text, max_length)
    
    def _fallback_summarize(self, text: str, max_length: int) -> str:
        """Fallback summarization using TF-IDF method"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from nltk.tokenize import sent_tokenize
            import numpy as np
            
            sentences = sent_tokenize(text)
            
            if len(sentences) == 0:
                return text[:500]
            
            # Create TF-IDF matrix
            vectorizer = TfidfVectorizer(max_features=50)
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Sum TF-IDF scores for each sentence
            sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
            
            # Select top sentences
            num_sentences = max(1, int(len(sentences) * 0.3))
            top_indices = np.argsort(sentence_scores)[-num_sentences:][::-1]
            top_indices = sorted(top_indices)
            
            # Create summary
            summary = ' '.join([sentences[i] for i in top_indices])
            
            # Truncate to max_length if needed
            if len(summary.split()) > max_length:
                summary = ' '.join(summary.split()[:max_length])
            
            return summary
        except Exception as e:
            logger.error(f"Error in fallback summarization: {e}")
            return text[:500]
    
    def generate_abstract(self, text: str) -> str:
        """Generate an abstract summary (shorter version)"""
        return self.summarize(text, max_length=150)
