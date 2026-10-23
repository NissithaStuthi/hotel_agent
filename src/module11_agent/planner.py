"""Module 11: Agent Planning & Decision Making Engine

Deconstructs guest inquiries into structured plans:
1. Deconstructs request into goals & tasks
2. Determines required subsystem: Hotel KB, Hotel Services, Local Info, or Action
3. Generates ordered PlanSteps
4. Deliberates next action based on agent state and intermediate tool outputs
"""

import re
from typing import List, Dict, Any, Optional
from src.module11_agent.models import (
    AgentPlan,
    PlanStep,
    AgentDecision,
    ActionType,
    AgentState,
    AgentStepStatus
)


class AgentPlanner:
    """Intelligent Planner for the Concierge Agent."""

    def __init__(self):
        pass

    def create_plan(self, query: str, state: AgentState) -> AgentPlan:
        """Analyzes guest query and synthesizes an execution plan."""
        q = query.strip()
        ql = q.lower()

        # Check for service request actions (towels, housekeeping, maintenance, late checkout request)
        if any(w in ql for w in ["need", "bring", "send", "extra towel", "towels", "housekeeping", "clean my room", "late checkout", "late check-out", "pillow", "water", "broken", "fix"]):
            # Action: Service Request
            steps = [
                PlanStep(
                    step_id=1,
                    description="Extract service parameters and verify room number",
                    subsystem="services",
                    tool_name="create_service_request",
                    parameters={"query": q}
                )
            ]
            return AgentPlan(goal=f"Fulfill guest service request: '{q}'", complexity="simple", steps=steps)

        # Check for Itinerary / Travel Planning (Compound / Multi-Step)
        if any(w in ql for w in ["itinerary", "plan something", "plan a day", "free day", "day trip", "schedule for tomorrow", "what can i do tomorrow"]):
            steps = [
                PlanStep(
                    step_id=1,
                    description="Retrieve top attractions and cultural highlights",
                    subsystem="local_info",
                    tool_name="search_attractions",
                    parameters={"query": "top scenic attractions and culture", "max_distance_km": 15.0}
                ),
                PlanStep(
                    step_id=2,
                    description="Calculate proximity distances and transit between selected sites",
                    subsystem="local_info",
                    tool_name="calculate_distance",
                    parameters={"origin": "The Grand Azure Resort", "destination": "Historic Old Town Citadel"}
                ),
                PlanStep(
                    step_id=3,
                    description="Recommend dining options near scheduled attractions",
                    subsystem="local_info",
                    tool_name="get_restaurant_info",
                    parameters={"meal_type": "lunch"}
                ),
                PlanStep(
                    step_id=4,
                    description="Synthesize cohesive time-slotted day itinerary",
                    subsystem="local_info",
                    tool_name="synthesize_itinerary",
                    parameters={"pace": "balanced"}
                )
            ]
            return AgentPlan(goal="Generate curated full-day travel itinerary", complexity="multi_step", steps=steps)

        # Check for Dining inquiries & Recommendations
        if any(w in ql for w in ["restaurant", "dining", "dinner", "lunch", "breakfast", "food", "menu", "cuisine", "table", "book a table", "reserve a table"]):
            steps = [
                PlanStep(
                    step_id=1,
                    description="Lookup resort and regional dining venues matching preferences",
                    subsystem="hotel_kb",
                    tool_name="get_restaurant_info",
                    parameters={"query": q}
                )
            ]
            return AgentPlan(goal="Provide tailored restaurant recommendation and dining details", complexity="simple", steps=steps)

        # Check for Room information / Suites
        if any(w in ql for w in ["room", "suite", "villa", "penthouse", "bed", "occupancy", "view", "rate", "upgrade"]):
            steps = [
                PlanStep(
                    step_id=1,
                    description="Retrieve detailed room specifications, rates, and amenities",
                    subsystem="hotel_kb",
                    tool_name="get_room_info",
                    parameters={"query": q}
                )
            ]
            return AgentPlan(goal="Provide room and suite accommodations information", complexity="simple", steps=steps)

        # Check for Hotel Policies & Check-in/Check-out
        if any(w in ql for w in ["policy", "check-in", "check in", "check-out", "checkout", "cancellation", "pet", "smoking", "deposit"]):
            steps = [
                PlanStep(
                    step_id=1,
                    description="Consult official resort policies and terms",
                    subsystem="hotel_kb",
                    tool_name="get_hotel_policy",
                    parameters={"query": q}
                )
            ]
            return AgentPlan(goal="Retrieve hotel policy and regulation facts", complexity="simple", steps=steps)

        # Check for Local Attractions / Sightseeing
        if any(w in ql for w in ["attraction", "sights", "visit", "things to do", "explore", "beach", "cove", "shopping", "museum"]):
            steps = [
                PlanStep(
                    step_id=1,
                    description="Search local destination attractions and activities",
                    subsystem="local_info",
                    tool_name="search_attractions",
                    parameters={"query": q}
                )
            ]
            return AgentPlan(goal="Discover local attractions and activities", complexity="simple", steps=steps)

        # Check for specific Hotel Services (Spa, Pool, Gym, Laundry, Wi-Fi, Parking)
        if any(w in ql for w in ["spa", "massage", "pool", "gym", "fitness", "laundry", "dry clean", "wifi", "internet", "parking", "valet"]):
            steps = [
                PlanStep(
                    step_id=1,
                    description="Query specialized hotel service knowledge base",
                    subsystem="services",
                    tool_name="search_hotel_services",
                    parameters={"query": q}
                )
            ]
            return AgentPlan(goal="Retrieve specific hotel service guidelines and hours", complexity="simple", steps=steps)

        # General conversational or compound query
        steps = [
            PlanStep(
                step_id=1,
                description="General concierge knowledge lookup",
                subsystem="hotel_kb",
                tool_name="get_hotel_policy",
                parameters={"query": q}
            )
        ]
        return AgentPlan(goal=f"Assist guest with: '{q}'", complexity="simple", steps=steps)

    def decide_next_action(self, state: AgentState) -> AgentDecision:
        """Deliberates next action based on active plan and collected observations."""
        # 1. If waiting for user clarification / slot (e.g. room number)
        if state.pending_slot:
            return AgentDecision(
                action_type=ActionType.ASK_CLARIFICATION,
                reasoning=f"Awaiting required slot: {state.pending_slot}",
                clarification_question=f"Could you please confirm your {state.pending_slot.replace('_', ' ')}?"
            )

        # 2. Check active plan
        plan = state.active_plan
        if not plan or plan.completed:
            return AgentDecision(
                action_type=ActionType.RESPOND,
                reasoning="Plan completed or no active plan. Synthesizing final response.",
                confidence=1.0
            )

        current_step = plan.get_current_step()
        if not current_step:
            return AgentDecision(
                action_type=ActionType.RESPOND,
                reasoning="All plan steps evaluated.",
                confidence=1.0
            )

        # 3. Step requires tool execution
        return AgentDecision(
            action_type=ActionType.CALL_TOOL,
            reasoning=f"Executing plan step {current_step.step_id}: {current_step.description}",
            tool_name=current_step.tool_name,
            tool_args=current_step.parameters,
            confidence=0.95
        )
