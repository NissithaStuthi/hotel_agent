"""Module 5: ChromaDB Persistent Vector Store Manager

Ingests chunks from knowledge documents, creates embeddings, and performs
vector similarity search with metadata filtering.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from src.config import CHROMA_PERSIST_DIR, KNOWLEDGE_DOCS_DIR, CHROMA_COLLECTION_NAME, DEFAULT_TOP_K
from src.module5_rag.chunker import HotelKnowledgeChunker, KnowledgeChunk


class HotelVectorStore:
    """Manages ChromaDB vector indexing and retrieval for hotel knowledge."""

    def __init__(
        self,
        persist_dir: Path = CHROMA_PERSIST_DIR,
        collection_name: str = CHROMA_COLLECTION_NAME
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine", "description": "The Grand Azure Hotel Knowledge Vector Store"}
        )
        self.chunker = HotelKnowledgeChunker()

        # Ingest documents if collection is empty
        if self.collection.count() == 0:
            self.index_all_documents()

    def index_all_documents(self, docs_dir: Path = KNOWLEDGE_DOCS_DIR) -> int:
        """Chunks and indexes all markdown files into ChromaDB."""
        all_chunks: List[KnowledgeChunk] = []

        if not docs_dir.exists():
            return 0

        for md_file in sorted(docs_dir.glob("*.md")):
            chunks = self.chunker.chunk_markdown_file(md_file)
            all_chunks.extend(chunks)

        if not all_chunks:
            return 0

        # Upsert into ChromaDB
        self.collection.upsert(
            ids=[c.chunk_id for c in all_chunks],
            documents=[c.text for c in all_chunks],
            metadatas=[c.metadata for c in all_chunks]
        )

        return len(all_chunks)

    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Searches vector store for chunks matching the query."""
        where_filter = None
        if category_filter:
            where_filter = {"category": category_filter}

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                # Cosine distance to similarity score
                similarity = round(1.0 - float(dist), 3) if dist is not None else 0.8
                formatted_results.append({
                    "text": doc,
                    "metadata": meta,
                    "similarity": similarity,
                    "source": f"{meta.get('source_file', 'unknown')} | {meta.get('section_title', '')}"
                })

        return formatted_results

    def count(self) -> int:
        return self.collection.count()
