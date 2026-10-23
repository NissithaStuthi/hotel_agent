"""Module 2: Knowledge Base Manager

Loads, validates, and provides structured querying across all hotel data files
(Hotel Profile, Rooms, Dining, Spa, Amenities, Policies, Attractions, Transportation).
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any

from src.config import DATA_DIR, KNOWLEDGE_DOCS_DIR
from src.module2_kb.models import (
    HotelProfile,
    RoomType,
    Restaurant,
    SpaTreatment,
    Amenity,
    HotelPolicy,
    LocalAttraction,
    TransportationOption
)


class KnowledgeBaseManager:
    """Central repository manager for hotel knowledge."""

    def __init__(self, data_dir: Path = DATA_DIR, docs_dir: Path = KNOWLEDGE_DOCS_DIR):
        self.data_dir = data_dir
        self.docs_dir = docs_dir

        self.hotel_profile: Optional[HotelProfile] = None
        self.rooms: List[RoomType] = []
        self.restaurants: List[Restaurant] = []
        self.spa_treatments: List[SpaTreatment] = []
        self.amenities: List[Amenity] = []
        self.policies: List[HotelPolicy] = []
        self.attractions: List[LocalAttraction] = []
        self.transportation: List[TransportationOption] = []
        self.raw_markdown_docs: Dict[str, str] = {}

        self.load_all()

    def load_all(self) -> None:
        """Loads and validates all structured datasets and markdown documents."""
        # 1. Hotel Profile
        profile_path = self.data_dir / "hotel_profile.json"
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                self.hotel_profile = HotelProfile.model_validate(json.load(f))

        # 2. Rooms
        rooms_path = self.data_dir / "rooms.json"
        if rooms_path.exists():
            with open(rooms_path, "r", encoding="utf-8") as f:
                self.rooms = [RoomType.model_validate(item) for item in json.load(f)]

        # 3. Dining
        dining_path = self.data_dir / "dining.json"
        if dining_path.exists():
            with open(dining_path, "r", encoding="utf-8") as f:
                self.restaurants = [Restaurant.model_validate(item) for item in json.load(f)]

        # 4. Spa
        spa_path = self.data_dir / "spa.json"
        if spa_path.exists():
            with open(spa_path, "r", encoding="utf-8") as f:
                self.spa_treatments = [SpaTreatment.model_validate(item) for item in json.load(f)]

        # 5. Amenities
        amenities_path = self.data_dir / "amenities.json"
        if amenities_path.exists():
            with open(amenities_path, "r", encoding="utf-8") as f:
                self.amenities = [Amenity.model_validate(item) for item in json.load(f)]

        # 6. Policies
        policies_path = self.data_dir / "policies.json"
        if policies_path.exists():
            with open(policies_path, "r", encoding="utf-8") as f:
                self.policies = [HotelPolicy.model_validate(item) for item in json.load(f)]

        # 7. Attractions
        attractions_path = self.data_dir / "attractions.json"
        if attractions_path.exists():
            with open(attractions_path, "r", encoding="utf-8") as f:
                self.attractions = [LocalAttraction.model_validate(item) for item in json.load(f)]

        # 8. Transportation
        transport_path = self.data_dir / "transportation.json"
        if transport_path.exists():
            with open(transport_path, "r", encoding="utf-8") as f:
                self.transportation = [TransportationOption.model_validate(item) for item in json.load(f)]

        # 9. Markdown Knowledge Documents
        if self.docs_dir.exists():
            for doc_file in sorted(self.docs_dir.glob("*.md")):
                with open(doc_file, "r", encoding="utf-8") as f:
                    self.raw_markdown_docs[doc_file.name] = f.read()

    # Query APIs
    def filter_rooms(
        self,
        min_occupancy: Optional[int] = None,
        pet_friendly: Optional[bool] = None,
        max_rate: Optional[float] = None
    ) -> List[RoomType]:
        results = self.rooms
        if min_occupancy is not None:
            results = [r for r in results if r.max_occupancy >= min_occupancy]
        if pet_friendly is not None:
            results = [r for r in results if r.pet_friendly == pet_friendly]
        if max_rate is not None:
            results = [r for r in results if r.base_rate_usd <= max_rate]
        return results

    def filter_restaurants(
        self,
        cuisine_keyword: Optional[str] = None,
        dietary_option: Optional[str] = None
    ) -> List[Restaurant]:
        results = self.restaurants
        if cuisine_keyword:
            kw = cuisine_keyword.lower()
            results = [r for r in results if kw in r.cuisine_type.lower() or kw in r.name.lower()]
        if dietary_option:
            diet = dietary_option.lower()
            results = [
                r for r in results
                if any(diet in d.lower() for d in r.dietary_options)
            ]
        return results

    def find_policy(self, query: str) -> List[HotelPolicy]:
        q = query.lower()
        return [
            p for p in self.policies
            if q in p.title.lower() or q in p.category.lower() or q in p.summary.lower() or q in p.details.lower()
        ]

    def get_summary_stats(self) -> Dict[str, Any]:
        """Returns statistics of loaded items in the Knowledge Base."""
        return {
            "hotel_name": self.hotel_profile.name if self.hotel_profile else "Unknown",
            "total_rooms_cataloged": len(self.rooms),
            "total_restaurants": len(self.restaurants),
            "total_spa_treatments": len(self.spa_treatments),
            "total_amenities": len(self.amenities),
            "total_policies": len(self.policies),
            "total_attractions": len(self.attractions),
            "total_transport_options": len(self.transportation),
            "total_markdown_documents": len(self.raw_markdown_docs)
        }
