"""Module 17: Multi-Agent Concierge System - Models

Defines schemas for specialized agent roles, task delegation, routing decisions,
sub-agent outputs, and master multi-agent orchestration.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class AgentRole(str, Enum):
    CONCIERGE_SUPERVISOR = "concierge_supervisor"
    HOTEL_AGENT = "hotel_agent"
    DINING_AGENT = "dining_agent"
    TRAVEL_AGENT = "travel_agent"
    SERVICE_AGENT = "service_agent"
    LOCAL_AGENT = "local_agent"
    COMPLAINT_AGENT = "complaint_agent"


class SubAgentTask(BaseModel):
    task_id: str
    target_role: AgentRole
    query_slice: str
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 1


class SubAgentResult(BaseModel):
    task_id: str
    agent_role: AgentRole
    agent_name: str
    success: bool = True
    response_text: str
    actions_taken: List[str] = Field(default_factory=list)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0


class RoutingDecision(BaseModel):
    original_query: str
    primary_role: AgentRole
    is_multi_agent: bool = False
    collaborating_roles: List[AgentRole] = Field(default_factory=list)
    reasoning: str
    tasks: List[SubAgentTask] = Field(default_factory=list)


class MultiAgentConciergeResponse(BaseModel):
    original_query: str
    routing_decision: RoutingDecision
    sub_agent_results: List[SubAgentResult] = Field(default_factory=list)
    unified_response: str
    total_actions_dispatched: int = 0
    all_tickets_and_bookings: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    @property
    def master_response(self) -> str:
        return self.unified_response
