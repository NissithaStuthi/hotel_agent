"""Module 7: Hotel Service Knowledge Assistant - Data Models"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import time


class ServiceCategory(str, Enum):
    """Hotel service categories."""
    HOUSEKEEPING = "housekeeping"
    LAUNDRY = "laundry"
    ROOM_SERVICE = "room_service"
    WIFI = "wifi"
    PARKING = "parking"
    GYM = "gym"
    POOL = "pool"
    SPA = "spa"
    RESTAURANTS = "restaurants"
    CONCIERGE = "concierge"
    TRANSPORTATION = "transportation"
    BUSINESS_CENTER = "business_center"
    VALET = "valet"
    CHILDCARE = "childcare"


class ServiceAvailability(BaseModel):
    """Service availability schedule."""
    monday: str = "24/7"
    tuesday: str = "24/7"
    wednesday: str = "24/7"
    thursday: str = "24/7"
    friday: str = "24/7"
    saturday: str = "24/7"
    sunday: str = "24/7"
    holidays: Optional[str] = None
    notes: Optional[str] = None


class ServicePricing(BaseModel):
    """Service pricing structure."""
    base_price: float = 0.0
    currency: str = "USD"
    unit: str = "per_use"
    tiers: Dict[str, float] = Field(default_factory=dict)
    complimentary_for: List[str] = Field(default_factory=list)
    gratuity_included: bool = False


class ServiceRequest(BaseModel):
    """Guest service request."""
    category: ServiceCategory
    description: str
    room_number: Optional[str] = None
    guest_name: Optional[str] = None
    preferred_time: Optional[str] = None
    special_instructions: Optional[str] = None
    priority: str = "normal"
    status: str = "pending"


class HousekeepingService(BaseModel):
    """Housekeeping service details."""
    id: str
    name: str = "Housekeeping"
    description: str
    services: List[str] = Field(default_factory=list)
    schedule: ServiceAvailability
    pricing: ServicePricing
    requestable_items: List[str] = Field(default_factory=list)
    turnaround_times: Dict[str, str] = Field(default_factory=dict)
    policies: List[str] = Field(default_factory=list)
    contact: str


class LaundryService(BaseModel):
    """Laundry and dry cleaning service."""
    id: str
    name: str = "Laundry & Dry Cleaning"
    description: str
    services: List[str] = Field(default_factory=list)
    schedule: ServiceAvailability
    pricing: ServicePricing
    item_pricing: Dict[str, float] = Field(default_factory=dict)
    express_available: bool = True
    express_surcharge: float = 0.5
    turnaround_standard: str = "24 hours"
    turnaround_express: str = "4 hours"
    policies: List[str] = Field(default_factory=list)
    contact: str


class RoomServiceMenu(BaseModel):
    """Room service menu details."""
    id: str
    name: str = "In-Room Dining"
    description: str
    hours: ServiceAvailability
    menu_categories: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    pricing: ServicePricing
    delivery_time: str = "30-45 minutes"
    minimum_order: float = 0.0
    dietary_options: List[str] = Field(default_factory=list)
    policies: List[str] = Field(default_factory=list)
    contact: str


class WiFiService(BaseModel):
    """Wi-Fi service details."""
    id: str
    name: str = "High-Speed Internet"
    description: str
    networks: List[Dict[str, Any]] = Field(default_factory=list)
    coverage_areas: List[str] = Field(default_factory=list)
    speed_tiers: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    pricing: ServicePricing
    device_limit: int = 5
    support_contact: str


class ParkingService(BaseModel):
    """Parking and valet service."""
    id: str
    name: str = "Parking & Valet"
    description: str
    options: List[Dict[str, Any]] = Field(default_factory=list)
    pricing: ServicePricing
    ev_charging: bool = True
    ev_charging_fee: float = 0.0
    valet_hours: str = "24/7"
    self_park_hours: str = "24/7"
    policies: List[str] = Field(default_factory=list)
    contact: str


class GymService(BaseModel):
    """Fitness center/gym service."""
    id: str
    name: str = "Fitness Pavilion"
    description: str
    equipment: List[str] = Field(default_factory=list)
    classes: List[Dict[str, Any]] = Field(default_factory=list)
    hours: ServiceAvailability
    pricing: ServicePricing
    personal_training: bool = True
    personal_training_fee: float = 0.0
    age_restriction: int = 16
    policies: List[str] = Field(default_factory=list)
    contact: str


class PoolService(BaseModel):
    """Pool service details."""
    id: str
    name: str
    description: str
    pool_type: str
    features: List[str] = Field(default_factory=list)
    hours: ServiceAvailability
    pricing: ServicePricing
    towel_service: bool = True
    lifeguard_hours: Optional[str] = None
    age_policy: str = "All ages welcome; children under 12 must be supervised"
    policies: List[str] = Field(default_factory=list)
    contact: str


class BusinessCenterService(BaseModel):
    """Business center service."""
    id: str
    name: str = "Business Center"
    description: str
    services: List[str] = Field(default_factory=list)
    equipment: List[str] = Field(default_factory=list)
    hours: ServiceAvailability
    pricing: ServicePricing
    meeting_rooms: List[Dict[str, Any]] = Field(default_factory=list)
    printing_rates: Dict[str, float] = Field(default_factory=dict)
    policies: List[str] = Field(default_factory=list)
    contact: str


class ChildcareService(BaseModel):
    """Childcare/kids club service."""
    id: str
    name: str = "Kids Club"
    description: str
    age_range: str = "4-12 years"
    activities: List[str] = Field(default_factory=list)
    hours: ServiceAvailability
    pricing: ServicePricing
    reservation_required: bool = True
    max_capacity: int = 20
    staff_ratio: str = "1:5"
    policies: List[str] = Field(default_factory=list)
    contact: str


class ServiceKnowledgeBase(BaseModel):
    """Complete service knowledge base."""
    hotel_name: str
    last_updated: str
    housekeeping: HousekeepingService
    laundry: LaundryService
    room_service: RoomServiceMenu
    wifi: WiFiService
    parking: ParkingService
    gym: GymService
    pools: List[PoolService]
    spa: Dict[str, Any]
    restaurants: List[Dict[str, Any]]
    business_center: BusinessCenterService
    childcare: ChildcareService
    concierge_services: List[str] = Field(default_factory=list)


class ServiceQuery(BaseModel):
    """Query for service information."""
    category: Optional[ServiceCategory] = None
    query: str
    guest_context: Dict[str, Any] = Field(default_factory=dict)


class ServiceResponse(BaseModel):
    """Response with service information."""
    category: ServiceCategory
    answer: str
    details: Dict[str, Any] = Field(default_factory=dict)
    actionable: bool = False
    suggested_actions: List[str] = Field(default_factory=list)
    contact: Optional[str] = None