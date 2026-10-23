"""Module 14: Restaurant & Dining Agent — Models & Schemas

Defines structured dining venue models, seating categories, dietary filters,
preference profiles, and table reservation records.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class DiningQueryType(str, Enum):
    TIMINGS = "timings"
    CUISINE = "cuisine"
    MENU = "menu"
    DIETARY = "dietary"
    SEATING = "seating"
    ROOM_SERVICE = "room_service"
    RECOMMENDATION = "recommendation"
    RESERVATION = "reservation"
    GENERAL = "general"


class SeatingArea(BaseModel):
    """Specific seating section within a dining venue."""
    area_id: str
    name: str
    location_desc: str
    atmosphere: str
    view: str
    requires_advance_booking: bool = False


class DiningVenueDetails(BaseModel):
    """Complete specification of a resort or partner dining venue."""
    id: str
    name: str
    cuisine_type: str
    dining_style: str
    location: str
    hours: Dict[str, str]
    dress_code: str
    reservation_required: bool
    price_level: str
    signature_dishes: List[str] = Field(default_factory=list)
    dietary_options: List[str] = Field(default_factory=list)
    seating_areas: List[SeatingArea] = Field(default_factory=list)
    room_service_available: bool = False
    chef_notes: Optional[str] = None


class DiningPreferences(BaseModel):
    """Guest dining criteria profile."""
    cuisine: Optional[str] = None
    party_size: int = 2
    dietary_restrictions: List[str] = Field(default_factory=list)
    atmosphere_preference: Optional[str] = Field(default="scenic", description="'romantic', 'casual', 'family', 'scenic', 'lively'")
    budget_preference: Optional[str] = "luxury"
    meal_period: str = Field(default="dinner", description="'breakfast', 'lunch', 'dinner', 'brunch', 'late_night'")
    preferred_seating: Optional[str] = None


class DiningReservation(BaseModel):
    """Confirmed table reservation record."""
    reservation_id: str
    confirmation_code: str = Field(description="Unique code e.g. RES-AZURE-8392")
    venue_name: str
    guest_name: str
    room_number: str
    party_size: int
    reservation_date: str
    time_slot: str
    seating_area: str
    special_requests: Optional[str] = None
    status: str = "confirmed"
    created_at: str
