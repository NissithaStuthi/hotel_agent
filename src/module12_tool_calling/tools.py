"""Module 12: Invocable Local Python Tools & Tool Registry

Implements first-class local Python tools with typed schemas, execution logic,
and a centralized ToolRegistry:
1. get_room_info()
2. get_restaurant_info()
3. get_hotel_policy()
4. search_attractions()
5. calculate_distance()
6. create_service_request()
7. get_service_status()
8. search_hotel_services()
"""

import json
import time
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from src.config import DATA_DIR
from src.module12_tool_calling.models import ToolDefinition, ToolResult
from src.module13_service_agent.database import ServiceRequestDatabase
from src.module13_service_agent.models import ServiceCategory, ServicePriority


# ---------------------------------------------------------------------------
# Tool Implementations
# ---------------------------------------------------------------------------

def get_room_info(
    room_type: Optional[str] = None,
    max_guests: Optional[int] = None,
    view: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve specifications, rates, bedding, and features for hotel rooms & suites."""
    rooms_file = DATA_DIR / "rooms.json"
    if not rooms_file.exists():
        return []

    with open(rooms_file, "r", encoding="utf-8") as f:
        rooms = json.load(f)

    results = []
    for r in rooms:
        if room_type and room_type.lower() not in r.get("name", "").lower() and room_type.lower() not in r.get("tier", "").lower():
            continue
        if max_guests and r.get("max_occupancy", 1) < max_guests:
            continue
        if view and view.lower() not in r.get("view_type", "").lower():
            continue
        results.append(r)

    # If strict filter returned nothing, return all rooms
    return results if results else rooms


def get_restaurant_info(
    restaurant_name: Optional[str] = None,
    cuisine: Optional[str] = None,
    meal_type: Optional[str] = None,
    dietary: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve restaurant timings, menus, cuisine, dietary options, and dress codes."""
    dining_file = DATA_DIR / "dining.json"
    if not dining_file.exists():
        return []

    with open(dining_file, "r", encoding="utf-8") as f:
        venues = json.load(f)

    results = []
    for v in venues:
        if restaurant_name and restaurant_name.lower() not in v.get("name", "").lower():
            continue
        if cuisine and cuisine.lower() not in v.get("cuisine_type", "").lower():
            continue
        if meal_type:
            hours_keys = " ".join(v.get("hours", {}).keys()).lower()
            if meal_type.lower() not in hours_keys and "24/7" not in hours_keys:
                continue
        if dietary:
            diet_str = " ".join(v.get("dietary_options", [])).lower()
            if dietary.lower() not in diet_str:
                continue
        results.append(v)

    return results if results else venues


def get_hotel_policy(
    policy_name: Optional[str] = None,
    topic: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve hotel policies regarding check-in/out, cancellations, pets, smoking, or deposits."""
    policies_file = DATA_DIR / "policies.json"
    if not policies_file.exists():
        return []

    with open(policies_file, "r", encoding="utf-8") as f:
        policies = json.load(f)

    query = (policy_name or topic or "").lower()
    if not query:
        return policies

    results = []
    for p in policies:
        title = p.get("title", "").lower()
        summary = p.get("summary", "").lower()
        details = p.get("details", "").lower()
        if query in title or query in summary or query in details:
            results.append(p)

    return results if results else policies


def search_attractions(
    query: str = "",
    category: Optional[str] = None,
    max_distance_km: Optional[float] = None
) -> List[Dict[str, Any]]:
    """Search regional tourist attractions, natural sights, and local destinations."""
    dest_file = DATA_DIR / "local_destinations.json"
    if not dest_file.exists():
        return []

    with open(dest_file, "r", encoding="utf-8") as f:
        destinations = json.load(f)

    results = []
    ql = query.lower()
    for d in destinations:
        if category and category.lower() != "all" and d.get("category", "").lower() != category.lower():
            continue
        if max_distance_km and d.get("distance_km", 0.0) > max_distance_km:
            continue
        if ql:
            name = d.get("name", "").lower()
            subcat = d.get("sub_category", "").lower()
            highlights = " ".join(d.get("highlights", [])).lower()
            tips = d.get("concierge_tips", "").lower()
            if ql not in name and ql not in subcat and ql not in highlights and ql not in tips:
                # partial word match
                words = [w for w in ql.split() if len(w) > 3]
                if not any(w in name or w in highlights or w in subcat for w in words):
                    continue
        results.append(d)

    return results if results else destinations[:4]


def calculate_distance(
    origin: str = "The Grand Azure Resort & Spa",
    destination: str = ""
) -> Dict[str, Any]:
    """Calculate geographic distance, travel time, and transit options between locations."""
    dest_file = DATA_DIR / "local_destinations.json"
    destinations = []
    if dest_file.exists():
        with open(dest_file, "r", encoding="utf-8") as f:
            destinations = json.load(f)

    dl = destination.lower().strip()
    match = None
    # 1. Exact or substring match
    for d in destinations:
        if dl in d.get("name", "").lower() or d.get("name", "").lower() in dl:
            match = d
            break

    # 2. Highest word overlap match
    if not match:
        query_words = [w for w in dl.split() if len(w) > 3]
        best_overlap = 0
        for d in destinations:
            name_lower = d.get("name", "").lower()
            overlap = sum(1 for w in query_words if w in name_lower)
            if overlap > best_overlap:
                best_overlap = overlap
                match = d

    if match:
        dist_km = match.get("distance_km", 4.5)
        mins = match.get("travel_time_minutes", int(dist_km * 2.2))
        transit = match.get("transit_options", ["Resort House Shuttle", "Private Sedan"])
        return {
            "origin": origin,
            "destination": match.get("name"),
            "distance_km": dist_km,
            "travel_time_minutes": mins,
            "recommended_transit": transit,
            "concierge_note": match.get("concierge_tips", "Direct shuttle departs main lobby hourly.")
        }

    # Fallback heuristic distance
    return {
        "origin": origin,
        "destination": destination if destination else "Regional Point of Interest",
        "distance_km": 5.2,
        "travel_time_minutes": 15,
        "recommended_transit": ["Resort Private Mercedes Sedan", "Coastal Taxi"],
        "concierge_note": "Conveniently accessible within 15 minutes from the resort porte-cochère."
    }


def create_service_request(
    room_number: str,
    service_type: str,
    item_or_description: str,
    guest_name: str = "Esteemed Guest",
    priority: str = "normal"
) -> Dict[str, Any]:
    """Submit and store a guest service request (housekeeping, towels, amenities, maintenance) in database."""
    cat_map = {
        "housekeeping": ServiceCategory.HOUSEKEEPING,
        "laundry": ServiceCategory.LAUNDRY,
        "front_desk": ServiceCategory.FRONT_DESK,
        "maintenance": ServiceCategory.MAINTENANCE,
        "room_service": ServiceCategory.ROOM_SERVICE,
        "bell_desk": ServiceCategory.BELL_DESK
    }
    category = cat_map.get(service_type.lower(), ServiceCategory.HOUSEKEEPING)

    prio_map = {
        "low": ServicePriority.LOW,
        "normal": ServicePriority.NORMAL,
        "high": ServicePriority.HIGH,
        "urgent": ServicePriority.URGENT
    }
    prio = prio_map.get(priority.lower(), ServicePriority.NORMAL)

    db = ServiceRequestDatabase()
    req = db.create_request(
        room_number=str(room_number),
        category=category,
        requested_items=[item_or_description],
        notes=f"Auto-generated via Tool Calling: {item_or_description}",
        guest_name=guest_name,
        priority=prio,
        estimated_turnaround_minutes=15
    )

    return {
        "ticket_number": req.ticket_number,
        "status": req.status.value,
        "room_number": req.room_number,
        "category": req.category.value,
        "estimated_completion_time": req.estimated_completion_time,
        "message": f"Successfully registered service ticket {req.ticket_number} for Room {req.room_number}."
    }


def get_service_status(request_id: str) -> Dict[str, Any]:
    """Retrieve status and estimated delivery time for an existing service ticket."""
    db = ServiceRequestDatabase()
    req = db.get_request(request_id)
    if not req:
        return {"found": False, "error": f"Ticket '{request_id}' not found."}
    return {
        "found": True,
        "ticket_number": req.ticket_number,
        "room_number": req.room_number,
        "status": req.status.value,
        "category": req.category.value,
        "items": req.requested_items,
        "created_at": req.created_at,
        "estimated_completion_time": req.estimated_completion_time
    }


def search_hotel_services(
    service_name: str,
    query: Optional[str] = None
) -> Dict[str, Any]:
    """Look up operating hours, contact extensions, pricing, and rules for resort amenities & services."""
    services_file = DATA_DIR / "hotel_services.json"
    if not services_file.exists():
        return {}

    with open(services_file, "r", encoding="utf-8") as f:
        services = json.load(f)

    sn = service_name.lower().replace(" ", "_")
    matched_svc = None
    for k, v in services.items():
        if isinstance(v, dict) and (sn in k.lower() or k.lower() in sn):
            matched_svc = v
            break

    if not matched_svc:
        # Return summary of available services
        avail = [k for k, v in services.items() if isinstance(v, dict)]
        return {"available_services": avail}

    return matched_svc


def synthesize_itinerary(
    query: str = "Plan a full day itinerary",
    pace: str = "balanced",
    theme: Optional[str] = None
) -> Dict[str, Any]:
    """Synthesize a complete chronological day itinerary with attractions, routing, and dining."""
    from src.module15_itinerary_agent.itinerary_planner import TravelItineraryAgent
    agent = TravelItineraryAgent()
    itin, _ = agent.plan_day(query)
    return itin.model_dump()


# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Centralized catalog and dispatcher for all agent-invocable tools."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._executables: Dict[str, Callable] = {}
        self._register_default_tools()

    def register(self, definition: ToolDefinition, func: Callable) -> None:
        """Registers a tool definition and its python executable function."""
        self._tools[definition.name] = definition
        self._executables[definition.name] = func

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def get_schemas(self) -> List[Dict[str, Any]]:
        return [t.to_openai_schema() for t in self._tools.values()]

    def execute(self, tool_name: str, arguments: Dict[str, Any], call_id: str = "call_local") -> ToolResult:
        """Executes a tool with parameters and returns structured ToolResult."""
        if tool_name not in self._executables:
            return ToolResult(
                call_id=call_id,
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' is not registered."
            )

        start = time.perf_counter()
        func = self._executables[tool_name]
        try:
            res_data = func(**arguments)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ToolResult(
                call_id=call_id,
                tool_name=tool_name,
                success=True,
                data=res_data,
                execution_time_ms=round(elapsed_ms, 2)
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ToolResult(
                call_id=call_id,
                tool_name=tool_name,
                success=False,
                error=str(e),
                execution_time_ms=round(elapsed_ms, 2)
            )

    def _register_default_tools(self) -> None:
        # 1. get_room_info
        self.register(
            ToolDefinition(
                name="get_room_info",
                description="Look up specifications, rates, bedding, view types, and features for hotel rooms & suites.",
                parameters={
                    "type": "object",
                    "properties": {
                        "room_type": {"type": "string", "description": "e.g. 'Deluxe', 'Villa', 'Ocean', 'Suite'"},
                        "max_guests": {"type": "integer", "description": "Minimum guest capacity required"},
                        "view": {"type": "string", "description": "View preference e.g. 'Ocean', 'Garden'"}
                    }
                }
            ),
            get_room_info
        )

        # 2. get_restaurant_info
        self.register(
            ToolDefinition(
                name="get_restaurant_info",
                description="Look up restaurant hours, cuisine styles, menus, signature dishes, dress codes, and dietary options.",
                parameters={
                    "type": "object",
                    "properties": {
                        "restaurant_name": {"type": "string", "description": "Name of restaurant e.g. 'Azure Breeze'"},
                        "cuisine": {"type": "string", "description": "Cuisine style e.g. 'French', 'Seafood', 'Italian'"},
                        "meal_type": {"type": "string", "description": "Meal period e.g. 'breakfast', 'lunch', 'dinner'"},
                        "dietary": {"type": "string", "description": "Dietary option e.g. 'Gluten-Free', 'Vegetarian', 'Vegan'"}
                    }
                }
            ),
            get_restaurant_info
        )

        # 3. get_hotel_policy
        self.register(
            ToolDefinition(
                name="get_hotel_policy",
                description="Retrieve hotel policies regarding check-in/out, pet policies, cancellations, smoking, or deposits.",
                parameters={
                    "type": "object",
                    "properties": {
                        "policy_name": {"type": "string", "description": "e.g. 'Pet Policy', 'Cancellation Policy'"},
                        "topic": {"type": "string", "description": "Keyword e.g. 'checkout', 'pets', 'deposit'"}
                    }
                }
            ),
            get_hotel_policy
        )

        # 4. search_attractions
        self.register(
            ToolDefinition(
                name="search_attractions",
                description="Search regional tourist attractions, natural sights, museums, and local activities.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search topic e.g. 'caves', 'museum', 'coastal'"},
                        "category": {"type": "string", "description": "'attractions', 'shopping', 'activities'"},
                        "max_distance_km": {"type": "number", "description": "Maximum distance radius from resort in km"}
                    }
                }
            ),
            search_attractions
        )

        # 5. calculate_distance
        self.register(
            ToolDefinition(
                name="calculate_distance",
                description="Calculate travel distance, commute duration, and transit options between resort and destination.",
                parameters={
                    "type": "object",
                    "properties": {
                        "origin": {"type": "string", "description": "Origin location, default 'The Grand Azure Resort & Spa'"},
                        "destination": {"type": "string", "description": "Destination attraction or venue name"}
                    },
                    "required": ["destination"]
                }
            ),
            calculate_distance
        )

        # 6. create_service_request
        self.register(
            ToolDefinition(
                name="create_service_request",
                description="Submit and store a guest service request (housekeeping, towels, maintenance, room service) in database.",
                parameters={
                    "type": "object",
                    "properties": {
                        "room_number": {"type": "string", "description": "Guest Room or Villa Number e.g. '412'"},
                        "service_type": {"type": "string", "description": "'housekeeping', 'laundry', 'maintenance', 'room_service', 'front_desk'"},
                        "item_or_description": {"type": "string", "description": "Requested item or service details e.g. '2 extra bath towels'"},
                        "guest_name": {"type": "string", "description": "Guest name if known"},
                        "priority": {"type": "string", "description": "'low', 'normal', 'high', 'urgent'"}
                    },
                    "required": ["room_number", "service_type", "item_or_description"]
                }
            ),
            create_service_request
        )

        # 7. get_service_status
        self.register(
            ToolDefinition(
                name="get_service_status",
                description="Check delivery status and estimated completion for an existing service ticket code.",
                parameters={
                    "type": "object",
                    "properties": {
                        "request_id": {"type": "string", "description": "Ticket reference e.g. 'REQ-20261017-001'"}
                    },
                    "required": ["request_id"]
                }
            ),
            get_service_status
        )

        # 8. search_hotel_services
        self.register(
            ToolDefinition(
                name="search_hotel_services",
                description="Look up operating hours, extensions, and pricing for resort facilities (Spa, Gym, Pool, Valet, Wi-Fi).",
                parameters={
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string", "description": "Name of service e.g. 'spa', 'gym', 'pool', 'wifi', 'parking'"},
                        "query": {"type": "string", "description": "Specific question or item"}
                    },
                    "required": ["service_name"]
                }
            ),
            search_hotel_services
        )

        # 9. synthesize_itinerary
        self.register(
            ToolDefinition(
                name="synthesize_itinerary",
                description="Synthesize a complete chronological day itinerary with attractions, transit, and dining.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Itinerary theme or request"},
                        "pace": {"type": "string", "description": "'relaxed', 'balanced', 'active'"}
                    }
                }
            ),
            synthesize_itinerary
        )
