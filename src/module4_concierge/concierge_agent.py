"""Module 4: Basic Conversational Concierge Agent (Baseline)

Implements the conversational concierge agent using prompt engineering,
persona styling, and multi-turn state tracking without RAG grounding.
"""

from typing import Optional, List, Dict
from src.module4_concierge.persona import PersonaStyle, get_system_prompt
from src.module4_concierge.memory import ConversationalMemory, ChatMessage
from src.module4_concierge.llm_backend import LLMBackend


class BasicConciergeAgent:
    """Basic Conversational Concierge Agent."""

    def __init__(
        self,
        persona_style: PersonaStyle = PersonaStyle.LUXURY_CLEFS_D_OR,
        provider: str = "auto"
    ):
        self.persona_style = persona_style
        self.system_prompt = get_system_prompt(persona_style)
        self.memory = ConversationalMemory()
        self.llm = LLMBackend(provider=provider)

    def chat(self, user_message: str) -> str:
        """Processes a guest message and generates a persona-styled reply."""
        # 1. Store user message in memory
        self.memory.add_user_message(user_message)

        # 2. Prepare message history for generation
        history_messages = self.memory.get_messages()

        # 3. Generate response via LLM backend
        response_text = self.llm.generate_response(
            system_prompt=self.system_prompt,
            messages=history_messages
        )

        # 4. Store assistant response in memory
        self.memory.add_assistant_message(response_text)

        return response_text

    def set_persona(self, new_style: PersonaStyle) -> None:
        """Dynamically switches concierge persona."""
        self.persona_style = new_style
        self.system_prompt = get_system_prompt(new_style)

    def reset(self) -> None:
        """Clears conversational memory."""
        self.memory.clear()
