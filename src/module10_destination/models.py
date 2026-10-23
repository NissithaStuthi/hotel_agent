"""Module 10: Local Destination Assistant - Data Models"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DestinationCategory(str, Enum):
    ATTRACTIONS = "attractions"
    RESTAURANTS = "restaurants"
    SHOPPING = "shopping"
    TRANSPORTATION = "transportation"
    TOURIST_LOCATIONS = "tourist_locations"
    ACTIVITIES = "activities"


class DestinationItem(BaseModel):
    """A destination venue, site, or transit service."""
    id: str
    name: str
    category: DestinationCategory
    sub_category: str
    distance_km: float
    travel_time_minutes: int
    transit_options: List[str] = Field(default_factory=list)
    operating_hours: str
    price_level: str
    family_friendly: bool = True
    highlights: List[str] = Field(default_factory=list)
    concierge_tips: str
    address_or_area: str


class DestinationSearchResult(BaseModel):
    item: DestinationItem
    similarity_score: float
    matched_highlights: List[str] = Field(default_factory=list)


class DestinationSearchResponse(BaseModel):
    query: str
    category_filter: Optional[str] = None
    total_found: int
    results: List[DestinationSearchResult]


class ItineraryStop(BaseModel):
    time_slot: str
    item: DestinationItem
    activity_description: str
    transit_guidance: str


class CuratedItinerary(BaseModel):
    title: str
    theme: str
    recommended_for: str
    stops: List[ItineraryStop]
    total_duration_hours: float
    concierge_notes: str
