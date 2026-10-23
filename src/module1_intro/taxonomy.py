"""Module 1: AI Hotel Concierge Taxonomy & Framework

Covers:
- Architectural comparison: Traditional Chatbots vs GenAI Concierge vs Agentic AI
- Taxonomy of Hotel Guest Requests: Information, Recommendation, Action-Based
- Pre-built catalog of realistic hotel guest scenarios
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class RequestCategory(str, Enum):
    """Core categories of hotel guest requests."""
    INFORMATION = "Information"          # Factual, policy, schedule, facility queries
    RECOMMENDATION = "Recommendation"    # Tailored suggestions (dining, activities, gifts)
    ACTION_BASED = "Action-Based"        # Service booking, housekeeping request, maintenance
    COMPLAINT = "Complaint & Feedback"   # Service issues, billing disputes, noise complaints
    EMERGENCY = "Emergency & Escalation" # Medical, safety, urgent security needs


class RequestDomain(str, Enum):
    """Hotel operational domains."""
    FRONT_DESK = "Front Desk & Policies"
    ROOMS = "Rooms & Accommodation"
    DINING = "Restaurants & Room Service"
    SPA_WELLNESS = "Spa & Wellness"
    AMENITIES = "Hotel Facilities & Amenities"
    LOCAL_ATTRACTIONS = "Local Attractions & Sightseeing"
    TRANSPORTATION = "Transportation & Valet"
    HOUSEKEEPING = "Housekeeping & Supplies"
    MAINTENANCE = "Maintenance & Engineering"
    BILLING = "Billing & Payments"


class UrgencyLevel(str, Enum):
    """Urgency level of guest request."""
    LOW = "Low"          # General inquiries, future planning
    MEDIUM = "Medium"    # Standard requests within the day
    HIGH = "High"        # Immediate service needs (e.g., room key issue, missing towels)
    CRITICAL = "Critical"# Medical emergency, water leak, safety hazard


@dataclass
class GuestScenario:
    """Represents a realistic hotel guest scenario."""
    id: str
    guest_query: str
    category: RequestCategory
    domain: RequestDomain
    urgency: UrgencyLevel
    guest_context: str
    expected_action: str
    suitable_architecture: str  # "Traditional Chatbot", "GenAI Concierge", or "Agentic AI"


# Catalog of 15 diverse hotel guest scenarios
SCENARIO_CATALOG: List[GuestScenario] = [
    # 1. Information-based scenarios
    GuestScenario(
        id="SCN-001",
        guest_query="What time is check-in and check-out tomorrow?",
        category=RequestCategory.INFORMATION,
        domain=RequestDomain.FRONT_DESK,
        urgency=UrgencyLevel.LOW,
        guest_context="Arriving guest wanting to plan airport departure.",
        expected_action="Provide exact check-in (3:00 PM) and check-out (11:00 AM) times and late check-out policy.",
        suitable_architecture="Traditional Chatbot / RAG GenAI"
    ),
    GuestScenario(
        id="SCN-002",
        guest_query="What time does breakfast open at the Azure Breeze restaurant?",
        category=RequestCategory.INFORMATION,
        domain=RequestDomain.DINING,
        urgency=UrgencyLevel.LOW,
        guest_context="In-house guest planning breakfast meeting.",
        expected_action="State breakfast hours (6:30 AM - 10:30 AM weekdays, until 11:00 AM weekends) and dress code.",
        suitable_architecture="Traditional Chatbot / RAG GenAI"
    ),
    GuestScenario(
        id="SCN-003",
        guest_query="Is the infinity pool heated, and are kids allowed in the evening?",
        category=RequestCategory.INFORMATION,
        domain=RequestDomain.AMENITIES,
        urgency=UrgencyLevel.LOW,
        guest_context="Family staying on floor 4.",
        expected_action="Confirm pool temperature (82°F) and adult-only quiet hours starting at 8:00 PM.",
        suitable_architecture="RAG GenAI"
    ),
    GuestScenario(
        id="SCN-004",
        guest_query="What is your cancellation policy if I need to leave a day early?",
        category=RequestCategory.INFORMATION,
        domain=RequestDomain.FRONT_DESK,
        urgency=UrgencyLevel.MEDIUM,
        guest_context="Corporate traveler whose meetings concluded ahead of schedule.",
        expected_action="Explain 24-hour advance notice rule to avoid early departure penalty fees.",
        suitable_architecture="RAG GenAI"
    ),
    GuestScenario(
        id="SCN-005",
        guest_query="Do you offer high-speed Wi-Fi suitable for Zoom video calls in the rooms?",
        category=RequestCategory.INFORMATION,
        domain=RequestDomain.ROOMS,
        urgency=UrgencyLevel.LOW,
        guest_context="Remote worker guest checking bandwidth specs.",
        expected_action="Detail complimentary high-speed fiber Wi-Fi (150 Mbps) and premium tier.",
        suitable_architecture="Traditional Chatbot / RAG GenAI"
    ),

    # 2. Recommendation-based scenarios
    GuestScenario(
        id="SCN-006",
        guest_query="Can you recommend a romantic seafood restaurant nearby with ocean sunset views?",
        category=RequestCategory.RECOMMENDATION,
        domain=RequestDomain.DINING,
        urgency=UrgencyLevel.LOW,
        guest_context="Couple celebrating their 10th anniversary.",
        expected_action="Recommend in-house Azure Breeze Cliffside Terrace or local gem 'Le Petit Port' (5 min walk).",
        suitable_architecture="GenAI Concierge / Agentic AI"
    ),
    GuestScenario(
        id="SCN-007",
        guest_query="What are the best outdoor activities or hiking trails within a 20-minute drive?",
        category=RequestCategory.RECOMMENDATION,
        domain=RequestDomain.LOCAL_ATTRACTIONS,
        urgency=UrgencyLevel.LOW,
        guest_context="Active solo traveler seeking scenic nature routes.",
        expected_action="Suggest Azure Coastal Trail and Lighthouse Lookout with difficulty ratings and trail maps.",
        suitable_architecture="GenAI Concierge / Agentic AI"
    ),
    GuestScenario(
        id="SCN-008",
        guest_query="My wife loves deep tissue massages. What spa treatment should we book?",
        category=RequestCategory.RECOMMENDATION,
        domain=RequestDomain.SPA_WELLNESS,
        urgency=UrgencyLevel.MEDIUM,
        guest_context="Husband looking for a surprise anniversary spa booking.",
        expected_action="Suggest the 80-minute 'Azure Deep Mineral Recovery Massage' and Couples Hydrotherapy ritual.",
        suitable_architecture="GenAI Concierge"
    ),
    GuestScenario(
        id="SCN-009",
        guest_query="We have 2 kids under 8. What are fun, rainy-day family activities around here?",
        category=RequestCategory.RECOMMENDATION,
        domain=RequestDomain.LOCAL_ATTRACTIONS,
        urgency=UrgencyLevel.LOW,
        guest_context="Family stuck inside due to unexpected afternoon showers.",
        expected_action="Recommend the Marine Aquarium (10 mins away) and the Resort's Little Mariners Club playroom.",
        suitable_architecture="GenAI Concierge"
    ),

    # 3. Action-based / Service Request scenarios
    GuestScenario(
        id="SCN-010",
        guest_query="Could we please have 3 extra bath towels and 2 bottles of sparkling water sent to Room 412?",
        category=RequestCategory.ACTION_BASED,
        domain=RequestDomain.HOUSEKEEPING,
        urgency=UrgencyLevel.HIGH,
        guest_context="Guest in Room 412 after swimming.",
        expected_action="Create automated housekeeping ticket dispatched to Floor 4 attendant with 15-minute ETA.",
        suitable_architecture="Agentic AI (Tool Calling)"
    ),
    GuestScenario(
        id="SCN-011",
        guest_query="I need an executive airport transfer to the international airport for 2 passengers at 6:30 AM tomorrow.",
        category=RequestCategory.ACTION_BASED,
        domain=RequestDomain.TRANSPORTATION,
        urgency=UrgencyLevel.MEDIUM,
        guest_context="Guest departing tomorrow morning.",
        expected_action="Invoke booking tool to reserve Mercedes S-Class sedan, confirm flight number and quote fee ($85).",
        suitable_architecture="Agentic AI (Tool Calling + Confirmation)"
    ),
    GuestScenario(
        id="SCN-012",
        guest_query="Please book a table for 4 at Le Jardin Bistro tonight at 8:00 PM under Mr. Reynolds.",
        category=RequestCategory.ACTION_BASED,
        domain=RequestDomain.DINING,
        urgency=UrgencyLevel.MEDIUM,
        guest_context="Guest planning dinner with business partners.",
        expected_action="Check restaurant table availability via API, hold reservation, issue confirmation code.",
        suitable_architecture="Agentic AI (Tool Calling)"
    ),

    # 4. Complaint & Escalation scenarios
    GuestScenario(
        id="SCN-013",
        guest_query="The air conditioner in Room 305 is making a loud rattling noise and it's 78 degrees in here!",
        category=RequestCategory.COMPLAINT,
        domain=RequestDomain.MAINTENANCE,
        urgency=UrgencyLevel.HIGH,
        guest_context="Unhappy guest trying to rest before a morning presentation.",
        expected_action="Express empathy, dispatch priority maintenance engineer, offer room relocation if unresolved in 20 min.",
        suitable_architecture="Agentic AI (De-escalation + Ticket Dispatch)"
    ),
    GuestScenario(
        id="SCN-014",
        guest_query="I was charged twice for valet parking on my preliminary invoice.",
        category=RequestCategory.COMPLAINT,
        domain=RequestDomain.BILLING,
        urgency=UrgencyLevel.MEDIUM,
        guest_context="Guest reviewing mobile checkout folio.",
        expected_action="Verify PMS folio entries, reverse duplicate charge, send updated receipt to guest email.",
        suitable_architecture="Agentic AI (PMS Integration)"
    ),
    GuestScenario(
        id="SCN-015",
        guest_query="My mother slipped in the hallway near elevator B and hurt her wrist! Please send help immediately!",
        category=RequestCategory.EMERGENCY,
        domain=RequestDomain.FRONT_DESK,
        urgency=UrgencyLevel.CRITICAL,
        guest_context="Distressed guest reporting an injury.",
        expected_action="Immediately notify Manager on Duty and Hotel First Responder EMT, keep caller on line.",
        suitable_architecture="Agentic AI (Emergency Escalation Protocol)"
    )
]


# Architectural Comparison Data
ARCHITECTURAL_COMPARISON = {
    "Traditional Rule-Based Chatbot": {
        "Capabilities": [
            "Intent matching via rigid keywords or regex",
            "Canned static button responses",
            "Single-turn interactions",
            "Breaks when wording deviates from predefined pattern"
        ],
        "Limitations": [
            "Cannot handle complex or multi-part questions",
            "Zero contextual empathy or personalized tone",
            "Requires hundreds of manual intent-response rules",
            "Cannot reason or combine knowledge"
        ],
        "Hospitality Fit": "Poor (frustrates luxury guests expecting human-level warmth)"
    },
    "GenAI Concierge (LLM + RAG)": {
        "Capabilities": [
            "Natural language comprehension of nuanced guest phrasing",
            "Multi-turn conversational memory and empathetic tone",
            "Grounded responses retrieved from hotel knowledge base (RAG)",
            "Dynamic synthesis of personalized recommendations"
        ],
        "Limitations": [
            "Read-only knowledge access without action execution (unless equipped with tools)",
            "Risk of hallucinating non-existent policies without RAG grounding"
        ],
        "Hospitality Fit": "Excellent for 24/7 guest consultation and recommendations"
    },
    "Agentic AI Concierge (Autonomous Workflows + Tools)": {
        "Capabilities": [
            "Plans and executes multi-step workflows (Check availability -> Book -> Notify guest)",
            "Function calling to Property Management System (PMS), POS, and Housekeeping dispatch",
            "Proactive anticipation of guest needs (e.g. flight delay -> offer late check-out)",
            "Human-in-the-loop escalation for sensitive complaints or emergencies"
        ],
        "Limitations": [
            "Requires robust API integrations, idempotency safeguards, and permission controls"
        ],
        "Hospitality Fit": "State-of-the-art enterprise solution for high-end hospitality"
    }
}
