"""Module 2: Pydantic Data Models for Structured Hotel Knowledge Base"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class HotelProfile(BaseModel):
    name: str = Field(..., description="Hotel name")
    star_rating: int = Field(5, description="Star rating")
    tagline: str = Field(..., description="Marketing tagline")
    address: str = Field(..., description="Street address")
    city: str = Field(..., description="City / Region")
    phone: str = Field(..., description="Concierge phone")
    email: str = Field(..., description="Concierge email")
    check_in_time: str = Field("3:00 PM", description="Standard check-in time")
    check_out_time: str = Field("11:00 AM", description="Standard check-out time")
    total_rooms: int = Field(220, description="Total room inventory")
    description: str = Field(..., description="Overview description")


class RoomType(BaseModel):
    id: str
    name: str
    tier: str  # Deluxe, Executive, Suite, Villa, Penthouse
    square_meters: int
    bed_configuration: str
    max_occupancy: int
    base_rate_usd: float
    view_type: str
    features: List[str]
    smoking_allowed: bool = False
    pet_friendly: bool = False


class Restaurant(BaseModel):
    id: str
    name: str
    cuisine_type: str
    dining_style: str  # Fine Dining, Casual, Lounge, Cafe
    location: str
    hours: Dict[str, str]
    dress_code: str
    reservation_required: bool
    price_level: str  # $, $$, $$$, $$$$
    signature_dishes: List[str]
    dietary_options: List[str]
    room_service_available: bool = True


class SpaTreatment(BaseModel):
    id: str
    name: str
    category: str  # Massage, Facial, Body Treatment, Hydrotherapy
    duration_minutes: int
    price_usd: float
    description: str
    advance_booking_hours: int = 4


class Amenity(BaseModel):
    id: str
    name: str
    category: str  # Wellness, Recreation, Business, Services
    location: str
    operating_hours: str
    access_fee_usd: float = 0.0  # 0 if complimentary
    rules: List[str]


class HotelPolicy(BaseModel):
    id: str
    title: str
    category: str  # Check-in/out, Cancellation, Pets, Children, Smoking, Noise
    summary: str
    details: str
    strictness_level: str  # Standard, Strict, Flexible


class LocalAttraction(BaseModel):
    id: str
    name: str
    category: str  # Cultural, Nature, Dining, Shopping, Adventure
    distance_km: float
    travel_time_minutes: int
    recommended_duration: str
    description: str
    concierge_tips: str


class TransportationOption(BaseModel):
    id: str
    service_type: str  # Airport Transfer, Luxury Chauffeur, Shuttle, Rental, Taxi
    provider_name: str
    rate_description: str
    booking_lead_time: str
    description: str
