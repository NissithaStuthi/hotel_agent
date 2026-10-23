"""Module 9: Personalized Recommendations - Data Models"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass


class GuestProfile(BaseModel):
    """Guest preference profile for personalized recommendations."""
    guest_name: Optional[str] = None
    room_number: Optional[str] = None
    party_type: str = "standard"  # "family_with_children", "couple_romantic", "solo_wellness", "business"
    children_count: int = 0
    children_ages: List[int] = Field(default_factory=list)
    max_distance_km: float = 10.0
    budget_tier: str = "luxury"
    interests: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    special_occasion: Optional[str] = None
    preferred_time_of_day: Optional[str] = None


class RecommendationCandidate(BaseModel):
    """An attraction, amenity, or activity candidate for recommendation."""
    id: str
    name: str
    category: str
    location_type: str = "resort"  # "resort" or "nearby_destination"
    distance_km: float = 0.0
    travel_time_minutes: int = 0
    operating_hours: str = "9:00 AM - 6:00 PM"
    family_friendly: bool = True
    min_age: int = 0
    price_level: str = "$$"
    tags: List[str] = Field(default_factory=list)
    description: str
    insider_tips: str


class ScoredRecommendation(BaseModel):
    """A candidate scored and explained by the personalized engine."""
    candidate: RecommendationCandidate
    semantic_similarity: float = 0.0
    family_alignment_score: float = 1.0
    distance_score: float = 1.0
    hours_score: float = 1.0
    composite_score: float = 0.0
    personalization_reasoning: str


class RecommendationResponse(BaseModel):
    """Response returned by the personalized recommendation engine."""
    query: str
    guest_profile: GuestProfile
    recommendations: List[ScoredRecommendation]
    concierge_advice: str
