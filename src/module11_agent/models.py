"""Module 11: Concierge Agent Architecture — Models & Schemas

Defines core data structures for autonomous agent operations:
- AgentState: Tracks conversational context, goals, thoughts, and metrics.
- PlanStep: Individual actionable step in an agent plan.
- AgentPlan: Structured decomposition of a guest inquiry into ordered steps.
- AgentDecision: Deliberation output deciding next action (Call Tool vs Clarify vs Respond).
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AgentStepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ActionType(str, Enum):
    CALL_TOOL = "call_tool"
    ASK_CLARIFICATION = "ask_clarification"
    RESPOND = "respond"
    DELEGATE_SUBAGENT = "delegate_subagent"


class PlanStep(BaseModel):
    """Represents a discrete step within an agent's execution plan."""
    step_id: int
    description: str
    subsystem: str = Field(description="Target subsystem: 'hotel_kb', 'services', 'local_info', 'action'")
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: AgentStepStatus = AgentStepStatus.PENDING
    result: Optional[Any] = None
    execution_notes: Optional[str] = None


class AgentPlan(BaseModel):
    """Represents an agent's multi-step or single-step execution plan."""
    goal: str
    complexity: str = Field(default="simple", description="'simple' (1 step) or 'multi_step'")
    steps: List[PlanStep] = Field(default_factory=list)
    current_step_index: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    completed: bool = False

    def get_current_step(self) -> Optional[PlanStep]:
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def advance(self) -> None:
        self.current_step_index += 1
        if self.current_step_index >= len(self.steps):
            self.completed = True


class AgentDecision(BaseModel):
    """Result of an agent deliberation turn."""
    action_type: ActionType
    reasoning: str
    tool_name: Optional[str] = None
    tool_args: Dict[str, Any] = Field(default_factory=dict)
    clarification_question: Optional[str] = None
    direct_response: Optional[str] = None
    confidence: float = 1.0


class AgentThought(BaseModel):
    """A single thought/observation record in the agent's reasoning trace."""
    turn_index: int
    thought: str
    action_taken: Optional[str] = None
    observation: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentState(BaseModel):
    """Full operational state of the Concierge Agent."""
    session_id: str
    guest_name: Optional[str] = None
    room_number: Optional[str] = None
    guest_preferences: Dict[str, Any] = Field(default_factory=dict)
    conversation_turns: List[Dict[str, str]] = Field(default_factory=list)
    active_plan: Optional[AgentPlan] = None
    reasoning_trace: List[AgentThought] = Field(default_factory=list)
    intermediate_tool_outputs: List[Dict[str, Any]] = Field(default_factory=list)
    pending_slot: Optional[str] = None
    total_tool_calls: int = 0

    def add_user_message(self, message: str) -> None:
        self.conversation_turns.append({"role": "user", "content": message})

    def add_assistant_message(self, message: str) -> None:
        self.conversation_turns.append({"role": "assistant", "content": message})

    def log_thought(self, thought: str, action: Optional[str] = None, observation: Optional[str] = None) -> None:
        self.reasoning_trace.append(AgentThought(
            turn_index=len(self.conversation_turns),
            thought=thought,
            action_taken=action,
            observation=observation
        ))
