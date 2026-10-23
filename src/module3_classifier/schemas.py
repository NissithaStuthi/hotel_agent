"""Module 3: Pydantic Schemas for Guest Query Intent Classification"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class IntentCategory(str, Enum):
    INFORMATION = "Information"
    RECOMMENDATION = "Recommendation"
    ACTION_BASED = "Action-Based"
    COMPLAINT = "Complaint & Feedback"
    EMERGENCY = "Emergency & Escalation"


class DomainCategory(str, Enum):
    FRONT_DESK = "Front Desk & Policies"
    ROOMS = "Rooms & Accommodation"
    DINING = "Restaurants & Room Service"
    SPA_WELLNESS = "Spa & Wellness"
    AMENITIES = "Hotel Facilities & Amenities"
    ATTRACTIONS = "Local Attractions & Sightseeing"
    TRANSPORTATION = "Transportation & Valet"
    HOUSEKEEPING = "Housekeeping & Supplies"
    MAINTENANCE = "Maintenance & Engineering"
    BILLING = "Billing & Payments"


class UrgencyLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ExtractedEntities(BaseModel):
    room_number: Optional[str] = Field(None, description="Extracted room number (e.g. '412', 'Villa 3')")
    guest_name: Optional[str] = Field(None, description="Guest name if mentioned")
    party_size: Optional[int] = Field(None, description="Number of guests/people mentioned")
    target_time: Optional[str] = Field(None, description="Time mentioned (e.g. '8:00 PM', 'tomorrow 6:30 AM')")
    requested_items: List[str] = Field(default_factory=list, description="Items requested (e.g. 'towels', 'water')")
    dietary_preferences: List[str] = Field(default_factory=list, description="Dietary requirements")


class ClassificationResult(BaseModel):
    query: str
    intent_category: IntentCategory
    domain: DomainCategory
    urgency: UrgencyLevel
    confidence: float = Field(0.9, ge=0.0, le=1.0)
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    reasoning: str = Field(..., description="Explanation of why this intent and domain were selected")
    recommended_routing: str = Field(..., description="Target department or agent workflow")
