"""Module 6: Sentence Embeddings for Semantic Search"""

import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class HotelEmbedder:
    """Sentence embedder optimized for hotel/hospitality domain."""
    
    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self._model = None
        self._onnx_fn = None
        self._dimension: int = 384
    
    @property
    def model(self):
        if self._model is None and self._onnx_fn is None:
            try:
                # Try local fast Chroma ONNX embedding first for instant offline speed
                import chromadb.utils.embedding_functions as ef
                self._onnx_fn = ef.DefaultEmbeddingFunction()
                self._dimension = 384
                logger.info("Chroma Default ONNX Embedder loaded successfully.")
            except Exception:
                try:
                    logger.info(f"Loading embedding model: {self.model_name}")
                    self._model = SentenceTransformer(self.model_name)
                    self._dimension = self._model.get_sentence_embedding_dimension()
                except Exception as e:
                    logger.warning(f"Fallback embedder error: {e}")
        return self._model or self._onnx_fn
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    def encode(
        self, 
        texts: Union[str, List[str]], 
        normalize: bool = True,
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """Encode texts to embeddings."""
        if isinstance(texts, str):
            texts = [texts]
        
        _ = self.model
        if self._onnx_fn is not None:
            raw_embs = self._onnx_fn(texts)
            arr = np.array(raw_embs, dtype=np.float32)
            if normalize:
                norms = np.linalg.norm(arr, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                arr = arr / norms
            return arr

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=normalize,
            convert_to_numpy=True
        )
        return embeddings
    
    def encode_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """Encode a single text."""
        return self.encode(text, normalize=normalize)[0]
    
    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def batch_similarity(self, query: np.ndarray, candidates: np.ndarray) -> np.ndarray:
        """Compute similarity between query and multiple candidates."""
        return candidates @ query


class HospitalityEmbedder(HotelEmbedder):
    """Extended embedder with hospitality-specific enhancements."""
    
    RELAXATION_KEYWORDS = [
        "relax", "unwind", "calm", "peaceful", "serene", "tranquil",
        "spa", "massage", "wellness", "therapy", "treatment",
        "lounge", "bar", "cocktail", "drink", "evening",
        "pool", "swim", "water", "sunbath", "sun",
        "garden", "terrace", "outdoor", "nature", "view",
        "quiet", "silent", "private", "intimate", "romantic"
    ]
    
    def __init__(self, model_name: str = HotelEmbedder.DEFAULT_MODEL):
        super().__init__(model_name)
        self._relaxation_embeddings: np.ndarray = None
    
    def _get_relaxation_embeddings(self) -> np.ndarray:
        if self._relaxation_embeddings is None:
            self._relaxation_embeddings = self.encode(self.RELAXATION_KEYWORDS)
        return self._relaxation_embeddings
    
    def relaxation_relevance(self, text: str) -> float:
        """Score how relevant a text is to relaxation concepts."""
        text_emb = self.encode_single(text)
        relax_embs = self._get_relaxation_embeddings()
        similarities = self.batch_similarity(text_emb, relax_embs)
        return float(np.max(similarities))
    
    def enhance_query_for_relaxation(self, query: str) -> str:
        """Enhance a query with relaxation context for better retrieval."""
        base = query.lower()
        if any(kw in base for kw in ["relax", "unwind", "after dinner", "evening", "calm"]):
            return f"{query} spa lounge pool garden wellness peaceful quiet evening"
        return query