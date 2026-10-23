"""Module 12: Tool Calling — Models & Schemas

Defines core structures for tool declaration, dispatching, and result encapsulation.
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    name: str
    type: str  # "string", "integer", "number", "boolean", "array"
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[str]] = None


class ToolDefinition(BaseModel):
    """Specification of an invocable agent tool."""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(description="JSON Schema describing input arguments")
    return_description: str = "JSON object containing operation results"

    def to_openai_schema(self) -> Dict[str, Any]:
        """Formats tool for OpenAI-compatible function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def to_gemini_schema(self) -> Dict[str, Any]:
        """Formats tool for Google Gemini function declarations."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class ToolCall(BaseModel):
    """Represents a decided tool invocation by the agent or LLM."""
    call_id: str
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    rationale: Optional[str] = None


class ToolResult(BaseModel):
    """Encapsulates execution result from an invoked tool."""
    call_id: str
    tool_name: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)

    def summary(self) -> str:
        if self.success:
            count = len(self.data) if isinstance(self.data, list) else 1
            return f"Success: {self.tool_name} returned {count} item(s)"
        return f"Error in {self.tool_name}: {self.error}"
