"""Module 15: Travel & Itinerary Planning Agent — Models & Schemas

Defines structured itinerary profiles, chronological stops, transit estimates,
and multi-stop day plans.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PacePreference(str, Enum):
    RELAXED = "relaxed"    # Fewer stops, longer leisure intervals
    BALANCED = "balanced"  # Standard pacing, 3-4 highlights + dining
    ACTIVE = "active"      # High density, 5+ sights & activities


class ItineraryTheme(str, Enum):
    ROMANTIC_CULINARY = "romantic_culinary"
    FAMILY_COASTAL = "family_coastal"
    CULTURE_HERITAGE = "culture_heritage"
    ADVENTURE_NATURE = "adventure_nature"
    WELLNESS_SERENITY = "wellness_serenity"
    CUSTOM = "custom"


class GuestItineraryProfile(BaseModel):
    """Guest preferences and constraints for travel itinerary synthesis."""
    available_hours: float = 12.0
    start_time: str = "9:00 AM"
    end_time: str = "9:30 PM"
    party_type: str = "couples_romantic"
    party_size: int = 2
    theme: ItineraryTheme = ItineraryTheme.ROMANTIC_CULINARY
    pace: PacePreference = PacePreference.BALANCED
    dietary_restrictions: List[str] = Field(default_factory=list)
    preferred_transit: str = "Resort Private Mercedes Sedan & Eco-Boat"


class ItineraryStop(BaseModel):
    """A scheduled destination or dining stop within the day itinerary."""
    stop_number: int
    time_slot: str
    venue_name: str
    category: str  # "attraction", "lunch", "dinner", "activity", "sightseeing"
    activity_description: str
    duration_minutes: int
    distance_from_prev_km: float
    travel_time_prev_mins: int
    transit_mode: str
    curator_tip: str
    estimated_cost: str


class TravelItinerary(BaseModel):
    """Complete personalized day itinerary synthesized by the Concierge Agent."""
    itinerary_id: str
    title: str
    theme: str
    target_audience: str
    summary: str
    total_duration_hours: float
    total_distance_km: float
    stops: List[ItineraryStop] = Field(default_factory=list)
    transit_advice: str
    booking_instructions: str
    created_at: str
