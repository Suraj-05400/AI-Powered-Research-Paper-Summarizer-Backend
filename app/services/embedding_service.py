import logging
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for creating and managing embeddings using Sentence Transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize embedding service with a pre-trained model"""
        self.model = SentenceTransformer(model_name)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.embeddings = None
        self.chunks = []
    
    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Create embeddings for a list of text chunks"""
        try:
            logger.info(f"Creating embeddings for {len(chunks)} chunks...")
            embeddings = self.model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)
            logger.info(f"Embeddings created with shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.IndexFlatL2:
        """Build FAISS index from embeddings"""
        try:
            logger.info("Building FAISS index...")
            # Ensure embeddings are in float32 format
            embeddings = embeddings.astype(np.float32)
            
            # Create index
            index = faiss.IndexFlatL2(self.embedding_dimension)
            index.add(embeddings)
            
            logger.info(f"FAISS index created with {index.ntotal} vectors")
            return index
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}")
            raise
    
    def search(self, query: str, index: faiss.IndexFlatL2, chunks: List[str], k: int = 5) -> List[tuple]:
        """Search for similar chunks using FAISS"""
        try:
            # Create embedding for query
            query_embedding = self.model.encode([query], convert_to_numpy=True).astype(np.float32)
            
            # Search in index
            distances, indices = index.search(query_embedding, min(k, len(chunks)))
            
            # Return results with similarity scores
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(chunks):
                    similarity = 1 / (1 + distances[0][i])  # Convert distance to similarity
                    results.append((chunks[idx], similarity, int(idx)))
            
            return results
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise
    
    def save_index(self, index: faiss.IndexFlatL2, chunks: List[str], save_path: str):
        """Save FAISS index and chunks to disk"""
        try:
            os.makedirs(save_path, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(index, os.path.join(save_path, "index.faiss"))
            
            # Save chunks
            with open(os.path.join(save_path, "chunks.pkl"), 'wb') as f:
                pickle.dump(chunks, f)
            
            logger.info(f"Index and chunks saved to {save_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise
    
    def load_index(self, save_path: str) -> tuple:
        """Load FAISS index and chunks from disk"""
        try:
            # Load FAISS index
            index = faiss.read_index(os.path.join(save_path, "index.faiss"))
            
            # Load chunks
            with open(os.path.join(save_path, "chunks.pkl"), 'rb') as f:
                chunks = pickle.load(f)
            
            logger.info(f"Index and chunks loaded from {save_path}")
            return index, chunks
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            raise
