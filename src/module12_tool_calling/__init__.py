"""Module 12: Tool Calling Package."""

from src.module12_tool_calling.models import (
    ToolDefinition,
    ToolCall,
    ToolResult,
    ToolParameter
)
from src.module12_tool_calling.tools import (
    ToolRegistry,
    get_room_info,
    get_restaurant_info,
    get_hotel_policy,
    search_attractions,
    calculate_distance,
    create_service_request,
    get_service_status,
    search_hotel_services
)
from src.module12_tool_calling.tool_caller import LLMToolDispatcher

__all__ = [
    "ToolDefinition",
    "ToolCall",
    "ToolResult",
    "ToolParameter",
    "ToolRegistry",
    "LLMToolDispatcher",
    "get_room_info",
    "get_restaurant_info",
    "get_hotel_policy",
    "search_attractions",
    "calculate_distance",
    "create_service_request",
    "get_service_status",
    "search_hotel_services"
]
