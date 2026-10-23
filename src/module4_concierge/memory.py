"""Module 4: Conversational Memory & Guest Profile State Tracking"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class ChatMessage:
    role: str  # "system", "user", "assistant"
    content: str


class ConversationalMemory:
    """Manages multi-turn conversation history and guest session state."""

    def __init__(self, max_history_turns: int = 10):
        self.max_history_turns = max_history_turns
        self.messages: List[ChatMessage] = []
        self.guest_name: Optional[str] = None
        self.room_number: Optional[str] = None
        self.guest_preferences: List[str] = []

    def add_user_message(self, content: str) -> None:
        self.messages.append(ChatMessage(role="user", content=content))
        self._inspect_and_extract_context(content)
        self._trim_history()

    def add_assistant_message(self, content: str) -> None:
        self.messages.append(ChatMessage(role="assistant", content=content))
        self._trim_history()

    def add_system_message(self, content: str) -> None:
        self.messages.insert(0, ChatMessage(role="system", content=content))

    def get_messages(self) -> List[ChatMessage]:
        return self.messages

    def get_history_as_text(self) -> str:
        """Formats conversation for prompt injection."""
        lines = []
        for msg in self.messages:
            if msg.role != "system":
                prefix = "Guest" if msg.role == "user" else "Concierge Julian"
                lines.append(f"{prefix}: {msg.content}")
        return "\n".join(lines)

    def clear(self) -> None:
        self.messages.clear()
        self.guest_name = None
        self.room_number = None
        self.guest_preferences.clear()

    def _trim_history(self) -> None:
        # Keep recent turns while preserving system message if present
        sys_msgs = [m for m in self.messages if m.role == "system"]
        chat_msgs = [m for m in self.messages if m.role != "system"]
        if len(chat_msgs) > self.max_history_turns * 2:
            chat_msgs = chat_msgs[-self.max_history_turns * 2:]
        self.messages = sys_msgs + chat_msgs

    def _inspect_and_extract_context(self, content: str) -> None:
        """Extracts guest name, room number, or stated preferences from dialogue."""
        import re
        q = content.lower()

        # Name extraction e.g. "my name is Eleanor Vance", "I am Mr. Smith"
        name_match = re.search(r'(?:my name is|i am|this is)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)', content, re.IGNORECASE)
        if name_match:
            self.guest_name = name_match.group(1).strip()

        # Room number
        room_match = re.search(r'\b(?:room|suite|villa)\s+([0-9a-zA-Z]+)\b', q)
        if room_match:
            self.room_number = room_match.group(1).upper()

        # Preferences
        if "vegetarian" in q and "Vegetarian diet" not in self.guest_preferences:
            self.guest_preferences.append("Vegetarian diet")
        if "gluten-free" in q and "Gluten-free diet" not in self.guest_preferences:
            self.guest_preferences.append("Gluten-free diet")
        if "anniversary" in q and "Celebrating Anniversary" not in self.guest_preferences:
            self.guest_preferences.append("Celebrating Anniversary")
