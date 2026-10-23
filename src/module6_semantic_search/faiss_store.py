"""Module 6: FAISS Vector Store for Semantic Search"""

import faiss
import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

from .schemas import SearchDomain, SearchResult
from .embedder import HotelEmbedder

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """FAISS-based vector store for hotel semantic search."""
    
    def __init__(
        self, 
        embedder: HotelEmbedder,
        index_path: Optional[str] = None,
        metadata_path: Optional[str] = None
    ):
        self.embedder = embedder
        self.dimension = embedder.dimension
        self.index: faiss.Index = None
        self.metadata: List[Dict[str, Any]] = []
        self.index_path = index_path
        self.metadata_path = metadata_path
        self._initialized = False
    
    def initialize(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        """Initialize the index with texts and metadata."""
        logger.info(f"Building FAISS index with {len(texts)} documents...")
        
        embeddings = self.embedder.encode(texts, normalize=True, show_progress=True)
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings.astype(np.float32))
        
        self.metadata = metadatas
        self._initialized = True
        
        logger.info(f"FAISS index built. Total vectors: {self.index.ntotal}")
        
        if self.index_path and self.metadata_path:
            self.save()
    
    def add(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        """Add new documents to the index."""
        if not self._initialized:
            self.initialize(texts, metadatas)
            return
        
        embeddings = self.embedder.encode(texts, normalize=True)
        self.index.add(embeddings.astype(np.float32))
        self.metadata.extend(metadatas)
        
        if self.index_path and self.metadata_path:
            self.save()
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        domain_filter: Optional[SearchDomain] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """Search the index for similar documents."""
        if not self._initialized or self.index.ntotal == 0:
            return []
        
        query_emb = self.embedder.encode_single(query, normalize=True)
        query_emb = query_emb.astype(np.float32).reshape(1, -1)
        
        actual_k = min(top_k * 3, self.index.ntotal)
        scores, indices = self.index.search(query_emb, actual_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or score < min_score:
                continue
            
            meta = self.metadata[idx]
            domain = SearchDomain(meta.get("domain", "all"))
            
            if domain_filter and domain_filter != SearchDomain.ALL and domain != domain_filter:
                continue
            
            results.append(SearchResult(
                content=meta.get("content", ""),
                source=meta.get("source", "unknown"),
                domain=domain,
                score=float(score),
                chunk_id=meta.get("chunk_id", str(idx)),
                metadata={k: v for k, v in meta.items() if k not in ["content", "source", "domain", "chunk_id"]}
            ))
            
            if len(results) >= top_k:
                break
        
        return results
    
    def search_by_embedding(
        self, 
        query_emb: np.ndarray, 
        top_k: int = 5,
        domain_filter: Optional[SearchDomain] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """Search using a pre-computed embedding."""
        if not self._initialized or self.index.ntotal == 0:
            return []
        
        query_emb = query_emb.astype(np.float32).reshape(1, -1)
        actual_k = min(top_k * 3, self.index.ntotal)
        scores, indices = self.index.search(query_emb, actual_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or score < min_score:
                continue
            
            meta = self.metadata[idx]
            domain = SearchDomain(meta.get("domain", "all"))
            
            if domain_filter and domain_filter != SearchDomain.ALL and domain != domain_filter:
                continue
            
            results.append(SearchResult(
                content=meta.get("content", ""),
                source=meta.get("source", "unknown"),
                domain=domain,
                score=float(score),
                chunk_id=meta.get("chunk_id", str(idx)),
                metadata={k: v for k, v in meta.items() if k not in ["content", "source", "domain", "chunk_id"]}
            ))
            
            if len(results) >= top_k:
                break
        
        return results
    
    def save(self):
        """Save index and metadata to disk."""
        if self.index_path:
            faiss.write_index(self.index, self.index_path)
            logger.info(f"FAISS index saved to {self.index_path}")
        
        if self.metadata_path:
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            logger.info(f"Metadata saved to {self.metadata_path}")
    
    def load(self):
        """Load index and metadata from disk."""
        if self.index_path and Path(self.index_path).exists():
            self.index = faiss.read_index(self.index_path)
            logger.info(f"FAISS index loaded from {self.index_path}")
        
        if self.metadata_path and Path(self.metadata_path).exists():
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            logger.info(f"Metadata loaded from {self.metadata_path}")
        
        self._initialized = self.index is not None and len(self.metadata) > 0
    
    def count(self) -> int:
        """Return number of vectors in index."""
        return self.index.ntotal if self.index else 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        domains = {}
        for meta in self.metadata:
            domain = meta.get("domain", "unknown")
            domains[domain] = domains.get(domain, 0) + 1
        
        return {
            "total_vectors": self.count(),
            "dimension": self.dimension,
            "domains": domains,
            "initialized": self._initialized
        }


class HybridFAISSStore(FAISSVectorStore):
    """FAISS store with keyword boosting for hybrid search."""
    
    def __init__(self, *args, keyword_weight: float = 0.3, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword_weight = keyword_weight
        self._keyword_index: Dict[str, List[int]] = {}
    
    def initialize(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        super().initialize(texts, metadatas)
        self._build_keyword_index(texts)
    
    def add(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        super().add(texts, metadatas)
        self._build_keyword_index(texts)
    
    def _build_keyword_index(self, texts: List[str]):
        """Build inverted index for keyword matching."""
        self._keyword_index = {}
        for idx, text in enumerate(texts):
            words = set(text.lower().split())
            for word in words:
                if word not in self._keyword_index:
                    self._keyword_index[word] = []
                self._keyword_index[word].append(idx)
    
    def _keyword_score(self, query: str, content: str) -> float:
        """Compute keyword overlap score."""
        query_words = set(query.lower().split())
        if not query_words:
            return 0.0
        
        content_lower = content.lower()
        matches = sum(1 for word in query_words if word in content_lower)
        return matches / len(query_words)
    
    def hybrid_search(
        self, 
        query: str, 
        top_k: int = 5,
        domain_filter: Optional[SearchDomain] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """Combine semantic and keyword search."""
        semantic_results = self.search(query, top_k * 2, domain_filter, 0.0)
        
        for result in semantic_results:
            kw_score = self._keyword_score(query, result.content)
            result.score = (1 - self.keyword_weight) * result.score + self.keyword_weight * kw_score
        
        semantic_results.sort(key=lambda x: x.score, reverse=True)
        
        return [r for r in semantic_results if r.score >= min_score][:top_k]