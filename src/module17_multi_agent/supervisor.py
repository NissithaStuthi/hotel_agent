"""Module 17: Multi-Agent Concierge System - Supervisor

Orchestrates multi-agent routing, decomposition, concurrent delegation,
and synthesis for complex single-domain and compound hospitality requests.
"""

import re
import uuid
from typing import Dict, Any, List, Optional

from src.module17_multi_agent.models import (
    AgentRole,
    SubAgentTask,
    SubAgentResult,
    RoutingDecision,
    MultiAgentConciergeResponse,
)
from src.module17_multi_agent.specialized_agents import (
    BaseSpecializedAgent,
    HotelAgent,
    DiningAgent,
    TravelAgent,
    ServiceAgent,
    LocalAgent,
    ComplaintAgent,
)


class MultiAgentConciergeSupervisor:
    """Master Chief Concierge agent (Supervisor) coordinating specialized sub-agents."""

    def __init__(self):
        self.agents: Dict[AgentRole, BaseSpecializedAgent] = {
            AgentRole.HOTEL_AGENT: HotelAgent(),
            AgentRole.DINING_AGENT: DiningAgent(),
            AgentRole.TRAVEL_AGENT: TravelAgent(),
            AgentRole.SERVICE_AGENT: ServiceAgent(),
            AgentRole.LOCAL_AGENT: LocalAgent(),
            AgentRole.COMPLAINT_AGENT: ComplaintAgent(),
        }

    def route_query(
        self,
        query: str,
        room_number: Optional[str] = None,
        guest_name: Optional[str] = None,
    ) -> RoutingDecision:
        """Determines whether a query routes to a single specialized agent or requires multi-agent collaboration."""
        q_lower = query.lower()

        # Extract room number from query if available
        if not room_number:
            match = re.search(r'\b(?:room|suite)\s*#?\s*([0-9]{3,4})\b', q_lower)
            if match:
                room_number = match.group(1)

        detected_roles: List[AgentRole] = []
        task_slices: List[tuple[AgentRole, str]] = []

        # Check for Complaint indicators
        complaint_keywords = [
            "broken", "not working", "isn't working", "is not working",
            "doesn't work", "leak", "leaking", "noise", "noisy",
            "too warm", "too hot", "too cold", "complaint", "defective"
        ]
        if any(w in q_lower for w in complaint_keywords) or ("ac" in q_lower and ("work" in q_lower or "hot" in q_lower)):
            detected_roles.append(AgentRole.COMPLAINT_AGENT)
            task_slices.append((AgentRole.COMPLAINT_AGENT, query))

        # Check for Housekeeping / Service indicators
        if any(w in q_lower for w in ["towel", "blanket", "housekeeping", "clean", "pillow", "late checkout", "checkout late", "luggage", "iron"]):
            if AgentRole.SERVICE_AGENT not in detected_roles:
                detected_roles.append(AgentRole.SERVICE_AGENT)
                task_slices.append((AgentRole.SERVICE_AGENT, query))

        # Check for Dining / Restaurant indicators
        if any(w in q_lower for w in ["restaurant", "dinner", "breakfast", "lunch", "menu", "cuisine", "table for", "reserve a table", "dine", "chef"]):
            if AgentRole.DINING_AGENT not in detected_roles:
                detected_roles.append(AgentRole.DINING_AGENT)
                task_slices.append((AgentRole.DINING_AGENT, query))

        # Check for Itinerary / Full Day trip indicators
        if any(w in q_lower for w in ["plan something", "free day", "itinerary", "day trip", "tomorrow plan", "schedule my day"]):
            if AgentRole.TRAVEL_AGENT not in detected_roles:
                detected_roles.append(AgentRole.TRAVEL_AGENT)
                task_slices.append((AgentRole.TRAVEL_AGENT, query))

        # Check for Local Sights / Destinations
        if any(w in q_lower for w in ["attraction", "sights", "sight", "places to visit", "visit", "ferry", "shopping", "caves", "citadel", "island", "how far to"]):
            if AgentRole.LOCAL_AGENT not in detected_roles and AgentRole.TRAVEL_AGENT not in detected_roles:
                detected_roles.append(AgentRole.LOCAL_AGENT)
                task_slices.append((AgentRole.LOCAL_AGENT, query))

        # Default to Hotel Agent if nothing specific triggered
        if not detected_roles:
            detected_roles.append(AgentRole.HOTEL_AGENT)
            task_slices.append((AgentRole.HOTEL_AGENT, query))

        # Determine Primary & Collaborators
        primary_role = detected_roles[0]
        collaborating_roles = detected_roles[1:]
        is_multi = len(detected_roles) > 1

        reasoning = (
            f"Multi-agent collaboration orchestrated across: {', '.join([r.value for r in detected_roles])}"
            if is_multi else
            f"Directly routed to specialized {primary_role.value} for authoritative domain resolution."
        )

        tasks = []
        context = {
            "room_number": room_number or "Guest Suite",
            "guest_name": guest_name or "Esteemed Guest",
            "full_query": query,
        }

        for idx, (role, slice_text) in enumerate(task_slices):
            tasks.append(SubAgentTask(
                task_id=f"TASK-{uuid.uuid4().hex[:6].upper()}",
                target_role=role,
                query_slice=slice_text,
                context=context,
                priority=idx + 1,
            ))

        return RoutingDecision(
            original_query=query,
            primary_role=primary_role,
            is_multi_agent=is_multi,
            collaborating_roles=collaborating_roles,
            reasoning=reasoning,
            tasks=tasks,
        )

    def process_query(
        self,
        query: str,
        room_number: Optional[str] = None,
        guest_name: Optional[str] = None,
    ) -> MultiAgentConciergeResponse:
        """Executes the full multi-agent orchestration pipeline."""
        routing = self.route_query(query, room_number=room_number, guest_name=guest_name)

        sub_agent_results: List[SubAgentResult] = []
        all_actions: List[str] = []
        all_tickets: List[str] = []

        # Execute sub-agent tasks
        for task in routing.tasks:
            agent = self.agents.get(task.target_role)
            if agent:
                res = agent.handle_task(task)
                sub_agent_results.append(res)
                all_actions.extend(res.actions_taken)
                for act in res.actions_taken:
                    if "ticket" in act.lower() or "reservation" in act.lower():
                        all_tickets.append(act)

        # Synthesize Unified Response in Chief Concierge Julian's voice
        guest_salutation = f"Esteemed {guest_name}," if guest_name else "Delighted to assist you, esteemed guest."
        
        if routing.is_multi_agent:
            body_parts = []
            for res in sub_agent_results:
                header = f"### [{res.agent_name}]"
                body_parts.append(f"{header}\n{res.response_text.strip()}")

            actions_block = ""
            if all_actions:
                actions_block = "\n\n**Coordinated Concierge Actions:**\n" + "\n".join(f"✔ {a}" for a in all_actions)

            unified = (
                f"{guest_salutation} I have coordinated with our specialized departments to fulfill every facet "
                f"of your request with flawless precision.\n\n"
                f"{chr(10).join(body_parts)}"
                f"{actions_block}\n\n"
                f"Everything is being overseen directly from the Concierge Desk. Should your plans evolve, "
                f"simply dial `0` for immediate personal service."
            )
        else:
            single_result = sub_agent_results[0] if sub_agent_results else None
            unified = single_result.response_text if single_result else "I am at your absolute service."

        return MultiAgentConciergeResponse(
            original_query=query,
            routing_decision=routing,
            sub_agent_results=sub_agent_results,
            unified_response=unified,
            total_actions_dispatched=len(all_actions),
            all_tickets_and_bookings=all_tickets,
        )
