"""Module 5: Hybrid Knowledge Retriever

Fetches relevant hotel knowledge using semantic vector search and
domain-based filtering.
"""

from typing import List, Dict, Any, Optional
from src.module5_rag.vector_store import HotelVectorStore
from src.module3_classifier.schemas import DomainCategory


# Mapping from Module 3 domain category to vector chunk category
DOMAIN_TO_CHUNK_CATEGORY = {
    DomainCategory.FRONT_DESK: "Policies",
    DomainCategory.ROOMS: "Rooms",
    DomainCategory.DINING: "Dining",
    DomainCategory.SPA_WELLNESS: "Spa",
    DomainCategory.AMENITIES: "Amenities",
    DomainCategory.ATTRACTIONS: "Local & Transport",
    DomainCategory.TRANSPORTATION: "Local & Transport"
}


class HotelRetriever:
    """Retriever for grounded knowledge search."""

    def __init__(self, vector_store: Optional[HotelVectorStore] = None):
        self.vector_store = vector_store or HotelVectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        domain_hint: Optional[DomainCategory] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant knowledge chunks."""
        category_filter = None
        if domain_hint and domain_hint in DOMAIN_TO_CHUNK_CATEGORY:
            category_filter = DOMAIN_TO_CHUNK_CATEGORY[domain_hint]

        # First try filtered search if category hint exists
        results = []
        if category_filter:
            results = self.vector_store.search(
                query=query,
                top_k=top_k,
                category_filter=category_filter
            )

        # If filtered search gave fewer than top_k or no filter, execute broad search
        if len(results) < top_k:
            broad_results = self.vector_store.search(
                query=query,
                top_k=top_k,
                category_filter=None
            )
            # Merge avoiding duplicate chunks
            seen_sources = {r["source"] for r in results}
            for r in broad_results:
                if r["source"] not in seen_sources:
                    results.append(r)
                    seen_sources.add(r["source"])

        return results[:top_k]

    def format_context_block(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Formats retrieved chunks into a cited context block."""
        if not retrieved_chunks:
            return "No verified hotel documentation matched the query."

        context_parts = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            source_tag = f"[Source {idx}: {chunk.get('source', 'Hotel Manual')}]"
            context_parts.append(f"{source_tag}\n{chunk['text'].strip()}")

        return "\n\n---\n\n".join(context_parts)
