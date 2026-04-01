import logging
import os
from typing import List
import numpy as np
import pickle
import faiss

logger = logging.getLogger(__name__)

class EmbeddingService:
    # Class-level variable to store the model (Lazy Loading)
    _model = None

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
        self.index = None
        self.embeddings = None
        self.chunks = []

    @classmethod
    def get_model(cls, model_name):
        """Loads the model only when needed to save RAM during startup"""
        if cls._model is None:
            logger.info(f"Loading SentenceTransformer: {model_name}...")
            from sentence_transformers import SentenceTransformer
            cls._model = SentenceTransformer(model_name)
        return cls._model

    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Create embeddings using the lazy-loaded model"""
        try:
            model = self.get_model(self.model_name)
            logger.info(f"Creating embeddings for {len(chunks)} chunks...")
            # show_progress_bar=False saves a bit of processing overhead
            embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=False)
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
            
            
    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.IndexFlatL2:
    """Build a FAISS index from embeddings"""
        embeddings = embeddings.astype(np.float32)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        logger.info(f"FAISS index built with {index.ntotal} vectors")
        return index
    
    def search(self, query: str, index: faiss.IndexFlatL2, chunks: List[str], k: int = 5) -> List[tuple]:
        """Search using the lazy-loaded model"""
        try:
            model = self.get_model(self.model_name)
            query_embedding = model.encode([query], convert_to_numpy=True).astype(np.float32)
            
            distances, indices = index.search(query_embedding, min(k, len(chunks)))
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(chunks):
                    # Higher similarity = better match
                    similarity = 1 / (1 + distances[0][i])
                    results.append((chunks[idx], float(similarity), int(idx)))
            
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

    # ... keep your save_index and load_index methods as they are ...
