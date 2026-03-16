import os
import logging
from typing import List, Tuple
from pathlib import Path
import PyPDF2
from docx import Document
import time

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process various document types (PDF, DOCX, TXT, etc.)"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.doc'}
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            raise
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extract text from any supported file format"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return DocumentProcessor.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return DocumentProcessor.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            return DocumentProcessor.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    @staticmethod
    def validate_file(filename: str, file_size: int, max_size: int = 52428800) -> Tuple[bool, str]:
        """Validate file before processing"""
        file_extension = Path(filename).suffix.lower()
        
        if file_extension not in DocumentProcessor.ALLOWED_EXTENSIONS:
            return False, f"File type not supported. Allowed: {DocumentProcessor.ALLOWED_EXTENSIONS}"
        
        if file_size > max_size:
            return False, f"File size exceeds maximum limit of {max_size / (1024*1024):.2f}MB"
        
        return True, "File is valid"
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into chunks for processing"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def get_word_count(text: str) -> int:
        """Get word count from text"""
        return len(text.split())
    
    @staticmethod
    def get_metadata(file_path: str, file_size: int, processing_time: float, chunks_count: int) -> dict:
        """Generate metadata for processed document"""
        return {
            "file_path": file_path,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "processing_time_seconds": round(processing_time, 2),
            "chunks_count": chunks_count,
            "chunk_size": 500,
            "timestamp": str(time.time()),
            "language_detected": "en"  # Can enhance with language detection
        }
