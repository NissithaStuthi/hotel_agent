"""Module 8: Guest Context & Conversation Memory - Session State

Tracks multi-turn short-term context, slot-filling state, pending clarifications,
and guest profile preferences across active conversation sessions.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class DialogueTurn:
    turn_id: int
    user_message: str
    assistant_message: str
    resolved_query: Optional[str] = None
    intent: Optional[str] = None
    extracted_slots: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PendingClarification:
    field_name: str  # e.g., "cuisine", "party_size", "time", "room_service_item"
    question_asked: str
    parent_intent: str
    options: List[str] = field(default_factory=list)


@dataclass
class GuestPreferences:
    guest_name: Optional[str] = None
    room_number: Optional[str] = None
    party_type: Optional[str] = None  # e.g., "solo", "couple", "family_with_children"
    dietary: List[str] = field(default_factory=list)  # e.g., ["Italian", "Vegetarian", "Gluten-Free"]
    interests: List[str] = field(default_factory=list)  # e.g., ["fine dining", "wellness", "beach"]
    budget_tier: str = "luxury"
    special_occasions: List[str] = field(default_factory=list)  # e.g., ["Anniversary", "Birthday"]


class SessionState:
    """Maintains active session state, short-term context, and slot memory."""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id: str = session_id or str(uuid.uuid4())[:8]
        self.turns: List[DialogueTurn] = []
        self.active_intent: Optional[str] = None
        self.active_domain: Optional[str] = None
        self.context_slots: Dict[str, Any] = {}
        self.pending_clarification: Optional[PendingClarification] = None
        self.preferences: GuestPreferences = GuestPreferences()

    def add_turn(
        self,
        user_msg: str,
        assistant_msg: str,
        resolved_query: Optional[str] = None,
        intent: Optional[str] = None,
        slots: Optional[Dict[str, Any]] = None
    ) -> DialogueTurn:
        turn = DialogueTurn(
            turn_id=len(self.turns) + 1,
            user_message=user_msg,
            assistant_message=assistant_msg,
            resolved_query=resolved_query or user_msg,
            intent=intent or self.active_intent,
            extracted_slots=slots or {}
        )
        self.turns.append(turn)
        return turn

    def set_pending_clarification(
        self,
        field_name: str,
        question_asked: str,
        parent_intent: str,
        options: Optional[List[str]] = None
    ) -> None:
        self.pending_clarification = PendingClarification(
            field_name=field_name,
            question_asked=question_asked,
            parent_intent=parent_intent,
            options=options or []
        )

    def clear_pending_clarification(self) -> None:
        self.pending_clarification = None

    def update_slot(self, key: str, value: Any) -> None:
        self.context_slots[key] = value

    def get_slot(self, key: str, default: Any = None) -> Any:
        return self.context_slots.get(key, default)

    def get_recent_history(self, max_turns: int = 5) -> List[DialogueTurn]:
        return self.turns[-max_turns:]

    def get_history_summary(self) -> str:
        """Returns concise multi-turn summary for context injection."""
        lines = []
        for t in self.turns[-4:]:
            lines.append(f"Guest: {t.user_message}")
            lines.append(f"Concierge: {t.assistant_message}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "total_turns": len(self.turns),
            "active_intent": self.active_intent,
            "active_domain": self.active_domain,
            "context_slots": self.context_slots,
            "pending_clarification": self.pending_clarification.__dict__ if self.pending_clarification else None,
            "preferences": {
                "guest_name": self.preferences.guest_name,
                "room_number": self.preferences.room_number,
                "party_type": self.preferences.party_type,
                "dietary": self.preferences.dietary,
                "interests": self.preferences.interests,
                "special_occasions": self.preferences.special_occasions
            }
        }

    def reset(self) -> None:
        self.turns.clear()
        self.active_intent = None
        self.active_domain = None
        self.context_slots.clear()
        self.pending_clarification = None
        self.preferences = GuestPreferences()
