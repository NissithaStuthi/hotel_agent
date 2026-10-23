"""Module 13: Guest Service Request Agent — Models & Schemas

Defines structured request types, priorities, categories, and database models.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ServiceCategory(str, Enum):
    HOUSEKEEPING = "housekeeping"
    LAUNDRY = "laundry"
    FRONT_DESK = "front_desk"
    MAINTENANCE = "maintenance"
    ROOM_SERVICE = "room_service"
    BELL_DESK = "bell_desk"


class ServicePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ServiceRequestStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ServiceRequest(BaseModel):
    """Structured hotel guest service request stored in database."""
    request_id: str
    ticket_number: str = Field(description="Unique human-readable ticket code e.g. REQ-20261017-001")
    room_number: str
    guest_name: Optional[str] = "Esteemed Guest"
    category: ServiceCategory
    requested_items: List[str] = Field(default_factory=list)
    notes: str
    priority: ServicePriority = ServicePriority.NORMAL
    status: ServiceRequestStatus = ServiceRequestStatus.PENDING
    created_at: str
    estimated_turnaround_minutes: int = 15
    estimated_completion_time: str
    completed_at: Optional[str] = None


class RequestAnalysis(BaseModel):
    """Result of analyzing an incoming guest service request."""
    category: ServiceCategory
    requested_items: List[str] = Field(default_factory=list)
    room_number: Optional[str] = None
    priority: ServicePriority = ServicePriority.NORMAL
    missing_information: List[str] = Field(default_factory=list)
    is_complete: bool = False
    turnaround_estimate_mins: int = 15
    special_instructions: Optional[str] = None
