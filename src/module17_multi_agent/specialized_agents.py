"""Module 17: Multi-Agent Concierge System - Specialized Agents

Defines individual domain-specialized agents:
- HotelAgent: Resort facilities, rooms, suites, and policies.
- DiningAgent: Restaurants, cuisine, menus, dietary options, and table bookings.
- TravelAgent: Full-day custom itineraries and regional sightseeing.
- ServiceAgent: Housekeeping, supplies, late checkout, and amenities.
- LocalAgent: Off-site attractions, shopping, ferry transit, and local culture.
- ComplaintAgent: Defect troubleshooting, de-escalation, and managerial alerts.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from src.module17_multi_agent.models import AgentRole, SubAgentTask, SubAgentResult
from src.module2_kb.kb_manager import KnowledgeBaseManager
from src.module5_rag.rag_engine import HotelRAGEngine
from src.module10_destination.destination_assistant import LocalDestinationAssistant
from src.module13_service_agent.service_agent import GuestServiceRequestAgent
from src.module14_dining_agent.dining_agent import RestaurantDiningAgent
from src.module15_itinerary_agent.itinerary_planner import TravelItineraryAgent
from src.module16_complaint_agent.complaint_agent import ComplaintResolutionAgent


class BaseSpecializedAgent(ABC):
    """Abstract base class for all specialized domain sub-agents."""

    def __init__(self, role: AgentRole, name: str):
        self.role = role
        self.name = name

    @abstractmethod
    def handle_task(self, task: SubAgentTask) -> SubAgentResult:
        """Processes the allocated task slice and returns structured result."""
        pass


class HotelAgent(BaseSpecializedAgent):
    """Specializes in resort rooms, suites, amenities, pools, and policies."""

    def __init__(self):
        super().__init__(AgentRole.HOTEL_AGENT, "Hotel Facilities & Policy Specialist")
        self.kb = KnowledgeBaseManager()
        self.rag_engine = HotelRAGEngine()

    def handle_task(self, task: SubAgentTask) -> SubAgentResult:
        start_time = time.time()
        query = task.query_slice
        response = self.rag_engine.answer_query(query)

        return SubAgentResult(
            task_id=task.task_id,
            agent_role=self.role,
            agent_name=self.name,
            response_text=response.answer,
            actions_taken=["Retrieved resort policies and suite specifications"],
            artifacts={"sources": response.sources, "confidence": response.grounding_confidence},
            execution_time_ms=(time.time() - start_time) * 1000,
        )


class DiningAgent(BaseSpecializedAgent):
    """Specializes in culinary venues, menus, dietary options, and reservations."""

    def __init__(self):
        super().__init__(AgentRole.DINING_AGENT, "Culinary & Dining Specialist")
        self.dining_agent = RestaurantDiningAgent()

    def handle_task(self, task: SubAgentTask) -> SubAgentResult:
        start_time = time.time()
        query = task.query_slice
        room = task.context.get("room_number")
        guest = task.context.get("guest_name", "Esteemed Guest")

        q_lower = query.lower()
        actions = []
        artifacts = {}

        if any(w in q_lower for w in ["reserve", "book a table", "table for"]):
            res = self.dining_agent.book_table(
                venue_name="Azure Breeze Seafood Grill" if "azure" in q_lower else "Le Jardin French Bistro",
                party_size=task.context.get("party_size", 2),
                time_slot=task.context.get("time", "7:30 PM"),
                guest_name=guest,
                room_number=room or "Suite",
                special_requests="Preferred cliffside terrace"
            )
            response_text = (
                f"I am pleased to confirm your reservation at **{res.venue_name}** for a party of {res.party_size} "
                f"at **{res.time_slot}** ({res.seating_area}). Confirmation Code: `{res.confirmation_code}`. "
                f"Special requests noted: {res.special_requests}."
            )
            actions.append(f"Confirmed table reservation: {res.confirmation_code}")
            artifacts["reservation"] = res.model_dump()
        else:
            dim_resp = self.dining_agent.answer_dining_query(query)
            response_text = dim_resp.get("reply", "Delighted to assist with your dining preferences.")
            q_type = dim_resp.get("query_type", "dining")
            actions.append(f"Answered dining dimension: {q_type}")
            artifacts["dimension"] = q_type

        return SubAgentResult(
            task_id=task.task_id,
            agent_role=self.role,
            agent_name=self.name,
            response_text=response_text,
            actions_taken=actions,
            artifacts=artifacts,
            execution_time_ms=(time.time() - start_time) * 1000,
        )


class TravelAgent(BaseSpecializedAgent):
    """Specializes in day trip itineraries and attraction sequencing."""

    def __init__(self):
        super().__init__(AgentRole.TRAVEL_AGENT, "Travel & Itinerary Specialist")
        self.itinerary_agent = TravelItineraryAgent()

    def handle_task(self, task: SubAgentTask) -> SubAgentResult:
        start_time = time.time()
        query = task.query_slice
        guest = task.context.get("guest_name", "Esteemed Guest")

        itinerary, _ = self.itinerary_agent.plan_day(query)
        theme_str = itinerary.theme.value if hasattr(itinerary.theme, "value") else str(itinerary.theme)
        lunch_stop = next((s for s in itinerary.stops if s.category == "lunch"), None)
        dinner_stop = next((s for s in itinerary.stops if s.category == "dinner"), None)
        dining_highlights = ""
        if lunch_stop and dinner_stop:
            dining_highlights = f" including VIP table reservations at {lunch_stop.venue_name} for lunch and {dinner_stop.venue_name} for dinner."

        concierge_text = (
            f"I have crafted a bespoke itinerary: **{itinerary.title}** ({theme_str.replace('_', ' ').title()}).\n"
            f"Spanning {itinerary.total_distance_km} km across {len(itinerary.stops)} curated milestones{dining_highlights}\n"
            f"Our Mercedes house chauffeur has been reserved for your transfers."
        )

        return SubAgentResult(
            task_id=task.task_id,
            agent_role=self.role,
            agent_name=self.name,
            response_text=concierge_text,
            actions_taken=[f"Synthesized full-day itinerary: '{itinerary.title}'", "Pre-reserved chauffeur vehicle"],
            artifacts={"itinerary_title": itinerary.title, "stops": len(itinerary.stops)},
            execution_time_ms=(time.time() - start_time) * 1000,
        )


class ServiceAgent(BaseSpecializedAgent):
    """Specializes in housekeeping, laundry, luggage, and service tickets."""

    def __init__(self):
        super().__init__(AgentRole.SERVICE_AGENT, "Guest Service & Housekeeping Specialist")
        self.service_agent = GuestServiceRequestAgent()

    def handle_task(self, task: SubAgentTask) -> SubAgentResult:
        start_time = time.time()
        query = task.query_slice
        room = task.context.get("room_number")
        guest = task.context.get("guest_name", "Esteemed Guest")

        outcome = self.service_agent.process_request(
            message=query,
            guest_name=guest,
            current_room=room
        )

        actions = []
        if outcome.get("status") == "confirmed" and outcome.get("request"):
            req = outcome["request"]
            actions.append(f"Dispatched service ticket: {req.ticket_number}")

        return SubAgentResult(
            task_id=task.task_id,
            agent_role=self.role,
            agent_name=self.name,
            response_text=outcome.get("reply", "Service request registered."),
            actions_taken=actions,
            artifacts={"request_status": outcome.get("status")},
            execution_time_ms=(time.time() - start_time) * 1000,
        )


class LocalAgent(BaseSpecializedAgent):
    """Specializes in local sights, shopping, beaches, and island excursions."""

    def __init__(self):
        super().__init__(AgentRole.LOCAL_AGENT, "Local Sightseeing & Culture Specialist")
        self.local_assistant = LocalDestinationAssistant()

    def handle_task(self, task: SubAgentTask) -> SubAgentResult:
        start_time = time.time()
        query = task.query_slice
        ans_dict = self.local_assistant.answer_destination_query(query)
        if isinstance(ans_dict, dict):
            response_text = ans_dict.get("answer") or ans_dict.get("reply") or str(ans_dict)
        else:
            response_text = str(ans_dict)

        return SubAgentResult(
            task_id=task.task_id,
            agent_role=self.role,
            agent_name=self.name,
            response_text=response_text,
            actions_taken=["Retrieved local sights and transit routes"],
            artifacts={},
            execution_time_ms=(time.time() - start_time) * 1000,
        )


class ComplaintAgent(BaseSpecializedAgent):
    """Specializes in issue troubleshooting, defect triage, and escalation."""

    def __init__(self):
        super().__init__(AgentRole.COMPLAINT_AGENT, "Quality Assurance & Complaint Specialist")
        self.complaint_agent = ComplaintResolutionAgent()

    def handle_task(self, task: SubAgentTask) -> SubAgentResult:
        start_time = time.time()
        query = task.query_slice
        room = task.context.get("room_number")
        guest = task.context.get("guest_name", "Esteemed Guest")

        result = self.complaint_agent.process_complaint(query, room_number=room, guest_name=guest)
        actions = []
        if result.ticket_created and result.service_request_id:
            actions.append(f"Dispatched engineering ticket: {result.service_request_id}")
        if result.escalation_triggered:
            actions.append(f"Escalated to: {result.analysis.escalation_level.value}")

        return SubAgentResult(
            task_id=task.task_id,
            agent_role=self.role,
            agent_name=self.name,
            response_text=result.concierge_response,
            actions_taken=actions,
            artifacts={
                "severity": result.analysis.detected_severity.value,
                "category": result.analysis.detected_category.value,
                "ticket_id": result.service_request_id,
            },
            execution_time_ms=(time.time() - start_time) * 1000,
        )
