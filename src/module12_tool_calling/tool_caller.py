"""Module 12: LLM Tool Decision & Dispatch Engine

Allows the LLM to decide which tool is required, extract parameters,
execute the tool, and synthesize a grounded response.
"""

import re
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple

from src.config import GEMINI_API_KEY, OPENAI_API_KEY
from src.module12_tool_calling.models import ToolDefinition, ToolCall, ToolResult
from src.module12_tool_calling.tools import ToolRegistry


class LLMToolDispatcher:
    """Dispatches natural language guest queries to tools via LLM decision-making."""

    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or ToolRegistry()

    def decide_tool(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[ToolCall]:
        """Analyzes query and decides which tool is required with extracted arguments."""
        q = query.strip()
        ql = q.lower()
        call_id = f"call_{uuid.uuid4().hex[:8]}"

        # 1. create_service_request
        if any(w in ql for w in ["need", "bring", "send", "extra towel", "towels", "housekeeping", "clean my room", "late checkout", "pillow"]):
            # Extract room number if present
            room = None
            r_match = re.search(r'\b(?:room|villa)\s*([0-9a-zA-Z]+)\b', ql)
            if r_match:
                room = r_match.group(1).upper()
            elif context and context.get("room_number"):
                room = context.get("room_number")

            if room:
                svc_type = "housekeeping"
                if "late check" in ql:
                    svc_type = "front_desk"
                elif "leak" in ql or "broken" in ql or "fix" in ql:
                    svc_type = "maintenance"
                return ToolCall(
                    call_id=call_id,
                    tool_name="create_service_request",
                    arguments={
                        "room_number": room,
                        "service_type": svc_type,
                        "item_or_description": q
                    },
                    rationale="Guest requested a hospitality service and provided room number."
                )

        # 2. get_service_status
        ticket_match = re.search(r'\b(REQ-[0-9]{8}-[0-9]{3})\b', q.upper())
        if ticket_match:
            return ToolCall(
                call_id=call_id,
                tool_name="get_service_status",
                arguments={"request_id": ticket_match.group(1)},
                rationale="Guest inquired about status of specific ticket."
            )

        # 3. calculate_distance
        if any(w in ql for w in ["distance", "how far", "travel time", "how to get to", "getting to", "transit to"]):
            dest = q
            for prefix in ["how far is", "how far to", "distance to", "how do we get to", "how to get to"]:
                if prefix in ql:
                    dest = ql.split(prefix)[-1].strip(" ?.")
                    break
            return ToolCall(
                call_id=call_id,
                tool_name="calculate_distance",
                arguments={"destination": dest.title()},
                rationale="Guest asked for travel distance/time to a local destination."
            )

        # 4. get_room_info
        if any(w in ql for w in ["room", "suite", "villa", "penthouse", "view", "rate", "bed"]):
            room_type = None
            for rt in ["deluxe", "presidential", "villa", "ocean", "penthouse", "family"]:
                if rt in ql:
                    room_type = rt.title()
                    break
            return ToolCall(
                call_id=call_id,
                tool_name="get_room_info",
                arguments={"room_type": room_type},
                rationale="Guest inquired about accommodations, suites, or room features."
            )

        # 5. search_hotel_services
        if any(w in ql for w in ["spa", "massage", "gym", "fitness", "pool", "wifi", "internet", "parking", "valet", "laundry"]):
            svc = "spa"
            for s in ["spa", "gym", "pool", "wifi", "parking", "laundry"]:
                if s in ql:
                    svc = s
                    break
            return ToolCall(
                call_id=call_id,
                tool_name="search_hotel_services",
                arguments={"service_name": svc, "query": q},
                rationale=f"Guest inquired about specialized hotel service: {svc}."
            )

        # 6. get_restaurant_info
        if any(w in ql for w in ["restaurant", "dining", "dinner", "lunch", "breakfast", "cuisine", "food", "menu", "seafood", "bistro", "wine"]):
            cuisine = None
            meal_type = None
            for c in ["seafood", "french", "italian", "mediterranean", "tapas"]:
                if c in ql:
                    cuisine = c.title()
                    break
            for m in ["breakfast", "lunch", "dinner", "brunch"]:
                if m in ql:
                    meal_type = m
                    break
            return ToolCall(
                call_id=call_id,
                tool_name="get_restaurant_info",
                arguments={"cuisine": cuisine, "meal_type": meal_type},
                rationale="Guest inquired about dining options, menus, or cuisine."
            )

        # 7. get_hotel_policy
        if any(w in ql for w in ["policy", "check-in", "check in", "check-out", "checkout", "cancellation", "pet", "smoking", "deposit"]):
            topic = "policy"
            if "pet" in ql:
                topic = "pet"
            elif "check" in ql:
                topic = "check-in"
            elif "cancel" in ql:
                topic = "cancellation"
            return ToolCall(
                call_id=call_id,
                tool_name="get_hotel_policy",
                arguments={"topic": topic},
                rationale="Guest inquired about official resort policies."
            )

        # 8. search_attractions
        if any(w in ql for w in ["attraction", "sights", "visit", "things to do", "explore", "cove", "old town", "museum", "shopping"]):
            return ToolCall(
                call_id=call_id,
                tool_name="search_attractions",
                arguments={"query": q, "max_distance_km": 15.0},
                rationale="Guest inquired about local sightseeing attractions."
            )

        # Default fallback tool
        return ToolCall(
            call_id=call_id,
            tool_name="get_hotel_policy",
            arguments={"topic": "general"},
            rationale="General knowledge consultation."
        )

    def execute_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[ToolCall], Optional[ToolResult]]:
        """Decides and executes tool for a query."""
        tool_call = self.decide_tool(query, context=context)
        if not tool_call:
            return None, None

        result = self.registry.execute(tool_call.tool_name, tool_call.arguments, call_id=tool_call.call_id)
        return tool_call, result
