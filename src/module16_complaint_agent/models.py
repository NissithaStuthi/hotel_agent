"""Module 16: Complaint & Issue Resolution Agent - Models

Defines structured data schemas for complaint classification, severity assessment,
troubleshooting guidance, service ticket generation, and managerial escalation.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ComplaintSeverity(str, Enum):
    LOW = "low"                # Minor amenity inconvenience (extra hanger, lightbulb)
    MEDIUM = "medium"          # Notable disruption (slow Wi-Fi, television remote)
    HIGH = "high"              # Serious comfort failure (AC down, no hot water, noise disturbance)
    CRITICAL = "critical"      # Emergency/safety hazard (flooding, door lock broken, power loss)


class ComplaintCategory(str, Enum):
    HVAC_AC = "hvac_air_conditioning"
    PLUMBING_WATER = "plumbing_water"
    ELECTRICAL_LIGHTING = "electrical_lighting"
    NOISE_DISTURBANCE = "noise_disturbance"
    CLEANLINESS_HOUSEKEEPING = "cleanliness_housekeeping"
    KEYCARD_ACCESS = "keycard_access"
    WIFI_TECHNOLOGY = "wifi_technology"
    AMENITY_DEFECT = "amenity_defect"
    BILLING_SERVICE = "billing_service"
    STAFF_INTERACTION = "staff_interaction"
    GENERAL = "general"


class EscalationLevel(str, Enum):
    NONE = "none"                            # Handled within standard resolution steps
    HOUSEKEEPING_SUPERVISOR = "housekeeping" # Housekeeping lead dispatch
    DUTY_ENGINEER = "duty_engineer"          # Immediate engineering dispatch
    GUEST_RELATIONS_MOD = "guest_relations"  # Manager on Duty (MOD) intervention
    EXECUTIVE_ASSISTANT = "executive"        # General Manager / Exec compensation


class TroubleshootingStep(BaseModel):
    step_number: int
    instruction: str
    rationale: str
    estimated_seconds: int = 30


class TroubleshootingGuide(BaseModel):
    category: ComplaintCategory
    issue_title: str
    symptoms: List[str]
    steps: List[TroubleshootingStep]
    success_criteria: str
    auto_dispatch_on_failure: bool = True
    estimated_fix_time_mins: int = 15


class ComplaintAnalysis(BaseModel):
    query: str
    detected_category: ComplaintCategory
    detected_severity: ComplaintSeverity
    room_number: Optional[str] = None
    guest_name: Optional[str] = None
    can_self_troubleshoot: bool = False
    requires_immediate_dispatch: bool = False
    escalation_level: EscalationLevel = EscalationLevel.NONE
    confidence: float = 0.95


class ComplaintResolutionResult(BaseModel):
    analysis: ComplaintAnalysis
    troubleshooting_guide: Optional[TroubleshootingGuide] = None
    suggested_steps: List[str] = Field(default_factory=list)
    service_request_id: Optional[str] = None
    ticket_created: bool = False
    escalation_triggered: bool = False
    escalation_details: Optional[Dict[str, Any]] = None
    apology_statement: str
    concierge_response: str
    follow_up_eta_minutes: int = 15
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
