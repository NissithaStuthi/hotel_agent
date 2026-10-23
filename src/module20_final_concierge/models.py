"""Module 20: Final AI Hotel Concierge Agent - Models

Defines the master telemetry, unified pipeline state, and execution manifest
for the complete end-to-end 8-stage hospitality agent.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.module3_classifier.schemas import ClassificationResult
from src.module11_agent.models import AgentPlan
from src.module17_multi_agent.models import RoutingDecision, SubAgentResult
from src.module18_multimodal.models import VisualAnalysisResult
from src.module19_safety_grounding.models import ValidatedAnswer, ValidationVerdict


class FinalSystemTelemetry(BaseModel):
    pipeline_duration_ms: float
    stages_completed: List[str] = Field(default_factory=list)
    specialized_agents_engaged: List[str] = Field(default_factory=list)
    tools_called: List[str] = Field(default_factory=list)
    grounding_verdict: ValidationVerdict = ValidationVerdict.GROUNDED_PASS
    confidence_score: float = 0.95
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class FinalConciergeResult(BaseModel):
    guest_name: str = "Esteemed Guest"
    room_number: Optional[str] = None
    original_query: str
    image_attached: Optional[str] = None
    intent_understanding: Optional[ClassificationResult] = None
    visual_analysis: Optional[VisualAnalysisResult] = None
    agent_plan: Optional[AgentPlan] = None
    routing_decision: Optional[RoutingDecision] = None
    sub_agent_results: List[SubAgentResult] = Field(default_factory=list)
    tools_executed: List[str] = Field(default_factory=list)
    service_tickets_created: List[str] = Field(default_factory=list)
    dining_reservations_made: List[str] = Field(default_factory=list)
    grounding_audit: Optional[ValidatedAnswer] = None
    final_response: str
    telemetry: FinalSystemTelemetry

    @property
    def response_text(self) -> str:
        return self.final_response
