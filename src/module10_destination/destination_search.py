"""Module 10: Local Destination Semantic Search Engine

Enables vector similarity search, category filtering, and distance constraints
across attractions, dining, shopping, transportation, sights, and activities.
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import chromadb

from src.config import CHROMA_PERSIST_DIR
from src.module10_destination.models import (
    DestinationCategory,
    DestinationItem,
    DestinationSearchResult,
    DestinationSearchResponse
)


class DestinationSemanticSearch:
    """Vector search engine across regional destinations and attractions."""

    def __init__(
        self,
        persist_dir: Path = CHROMA_PERSIST_DIR,
        data_path: Optional[Path] = None
    ):
        self.data_path = data_path or (Path("data") / "local_destinations.json")
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name="local_destinations_kb",
            metadata={"hnsw:space": "cosine"}
        )
        self.items: Dict[str, DestinationItem] = {}
        self._load_and_index()

    def _load_and_index(self) -> None:
        """Loads destination items and indexes them in ChromaDB."""
        if not self.data_path.exists():
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_list = json.load(f)

        self.items = {item["id"]: DestinationItem(**item) for item in raw_list}

        if self.collection.count() == 0:
            ids = []
            documents = []
            metadatas = []

            for item in self.items.values():
                content = (
                    f"Name: {item.name}\n"
                    f"Category: {item.category.value} - {item.sub_category}\n"
                    f"Distance: {item.distance_km} km ({item.travel_time_minutes} minutes)\n"
                    f"Transit Options: {', '.join(item.transit_options)}\n"
                    f"Hours: {item.operating_hours}\n"
                    f"Highlights: {', '.join(item.highlights)}\n"
                    f"Concierge Tips: {item.concierge_tips}\n"
                    f"Area: {item.address_or_area}"
                )
                ids.append(item.id)
                documents.append(content)
                metadatas.append({
                    "id": item.id,
                    "name": item.name,
                    "category": item.category.value,
                    "distance_km": float(item.distance_km),
                    "family_friendly": str(item.family_friendly)
                })

            self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def search(
        self,
        query: str,
        category: Optional[DestinationCategory] = None,
        max_distance_km: Optional[float] = None,
        top_k: int = 4
    ) -> DestinationSearchResponse:
        """Performs semantic search with optional category and distance filters."""
        where_filter = {}
        if category:
            where_filter["category"] = category.value

        query_kwargs: Dict[str, Any] = {
            "query_texts": [query],
            "n_results": min(top_k * 2, max(1, self.collection.count()))
        }
        if where_filter:
            query_kwargs["where"] = where_filter

        results = self.collection.query(**query_kwargs)

        scored_results: List[DestinationSearchResult] = []
        if results and results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            dists = results["distances"][0] if results.get("distances") else [0.2] * len(ids)

            for item_id, dist in zip(ids, dists):
                if item_id in self.items:
                    item = self.items[item_id]
                    if max_distance_km is not None and item.distance_km > max_distance_km:
                        continue

                    similarity = round(max(0.0, 1.0 - (dist / 2.0)), 3)
                    
                    # Highlight keyword matching
                    matched = [h for h in item.highlights if any(w in h.lower() for w in query.lower().split())]

                    scored_results.append(DestinationSearchResult(
                        item=item,
                        similarity_score=similarity,
                        matched_highlights=matched
                    ))

        # Sort descending by similarity
        scored_results.sort(key=lambda x: x.similarity_score, reverse=True)
        final_results = scored_results[:top_k]

        return DestinationSearchResponse(
            query=query,
            category_filter=category.value if category else None,
            total_found=len(final_results),
            results=final_results
        )

    def get_by_category(self, category: DestinationCategory) -> List[DestinationItem]:
        return [item for item in self.items.values() if item.category == category]
