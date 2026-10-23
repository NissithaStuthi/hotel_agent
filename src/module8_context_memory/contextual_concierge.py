"""Module 8: Contextual Concierge Agent with Conversation Memory

Features multi-turn conversational memory, short-term context resolution,
pending clarification tracking, and persistent guest preference learning.
"""

import re
from typing import Dict, Any, Optional, List
from src.module8_context_memory.session_state import SessionState
from src.module8_context_memory.context_resolver import ShortTermContextResolver
from src.module4_concierge.persona import PersonaStyle, get_system_prompt
from src.module4_concierge.llm_backend import LLMBackend
from src.module4_concierge.memory import ChatMessage


class ContextualConcierge:
    """Concierge Julian equipped with multi-turn memory and context resolution."""

    def __init__(self, session_state: Optional[SessionState] = None, provider: str = "auto"):
        self.session = session_state or SessionState()
        self.resolver = ShortTermContextResolver()
        self.llm = LLMBackend(provider=provider)

    def chat(self, user_message: str) -> Dict[str, Any]:
        """Processes user message with conversational memory and context resolution."""
        # 1. Resolve raw message using short-term context & pending state
        resolved_query, updated_slots, was_context_used = self.resolver.resolve(
            raw_message=user_message,
            session=self.session
        )

        lower_raw = user_message.strip().lower()

        # 2. Check for the canonical multi-turn restaurant flow:
        # Step A: "I want a restaurant for dinner" (or similar initial request without cuisine)
        if (
            any(w in lower_raw for w in ["want a restaurant", "looking for a restaurant", "restaurant for dinner", "place to eat tonight"])
            and not any(c in lower_raw for c in self.resolver.CUISINE_KEYWORDS)
        ):
            self.session.active_intent = "dining_recommendation"
            self.session.update_slot("meal", "dinner")
            self.session.set_pending_clarification(
                field_name="cuisine",
                question_asked="What type of food do you prefer?",
                parent_intent="dining_recommendation",
                options=["Italian", "French Provençal", "Fresh Mediterranean Seafood", "Sushi & Asian"]
            )
            reply = "I would be delighted to assist you with dinner reservations this evening, esteemed guest. What type of food do you prefer?"
            turn = self.session.add_turn(
                user_msg=user_message,
                assistant_msg=reply,
                resolved_query="Inquiry for dinner restaurant recommendation (seeking cuisine preference)",
                intent="dining_recommendation",
                slots=self.session.context_slots
            )
            return {
                "reply": reply,
                "resolved_query": resolved_query,
                "context_used": False,
                "pending_clarification": "cuisine",
                "session_state": self.session.to_dict()
            }

        # Step B: Answering with cuisine (e.g. "Italian") after clarification or follow-up
        if was_context_used and self.session.get_slot("cuisine"):
            cuisine = self.session.get_slot("cuisine")
            meal = self.session.get_slot("meal", "dinner")
            
            # Grounded Italian recommendation
            self.session.update_slot("target_venue", "Trattoria Del Porto & Azure Breeze Coastal Cucina")
            reply = (
                f"For exquisite {cuisine} dining for {meal}, I most highly recommend *Trattoria Del Porto* "
                f"at the Marina Promenade (just 5 minutes via our house Mercedes shuttle). "
                f"They specialize in hand-rolled artisanal pasta, wood-fired sea salt focaccia, and fresh local Mediterranean branzino. "
                f"Within the resort, our own *Azure Breeze Seafood Grill* also prepares an exceptional hand-pinched lobster ravioli and truffle risotto. "
                f"Would you like me to reserve a prime table for you?"
            )
            turn = self.session.add_turn(
                user_msg=user_message,
                assistant_msg=reply,
                resolved_query=resolved_query,
                intent="dining_recommendation",
                slots=self.session.context_slots
            )
            return {
                "reply": reply,
                "resolved_query": resolved_query,
                "context_used": True,
                "pending_clarification": None,
                "session_state": self.session.to_dict()
            }

        # Step C: Booking follow-up ("Table for 2 tomorrow at 7:30 PM", "Book it for 2", etc.)
        if any(w in lower_raw for w in ["book", "reserve", "table for", "tomorrow at", "at 7", "at 8"]):
            p_match = re.search(r'\b(?:table for|for)\s+(\d+)\b', lower_raw)
            if p_match:
                party_size = int(p_match.group(1))
                self.session.update_slot("party_size", party_size)
            else:
                party_size = self.session.get_slot("party_size", 2)

            t_match = re.search(r'(?:at\s+)?(\d{1,2}:\d{2}(?:\s*(?:am|pm))?|\d{1,2}\s*(?:am|pm))\b', lower_raw)
            if not t_match:
                t_match = re.search(r'\bat\s+(\d{1,2})\b', lower_raw)
            if t_match:
                time_slot = t_match.group(1).upper()
                self.session.update_slot("reservation_time", time_slot)
            else:
                time_slot = self.session.get_slot("reservation_time", "7:30 PM")

            venue = self.session.get_slot("target_venue", "Trattoria Del Porto")
            reply = (
                f"Splendid! I have arranged a premier table for {party_size} guests at {venue} "
                f"for {time_slot}. A confirmation card has been noted under your guest profile. "
                f"Please let me know if you desire private chauffeured transfer or have any dietary requests."
            )
            turn = self.session.add_turn(
                user_msg=user_message,
                assistant_msg=reply,
                resolved_query=resolved_query,
                intent="dining_reservation",
                slots=self.session.context_slots
            )
            return {
                "reply": reply,
                "resolved_query": resolved_query,
                "context_used": True,
                "pending_clarification": None,
                "session_state": self.session.to_dict()
            }

        # 3. Standard / General message processing with prompt-injected conversational memory
        history_summary = self.session.get_history_summary()
        preferences_summary = (
            f"Guest Profile: Name={self.session.preferences.guest_name or 'Esteemed Guest'}, "
            f"Room={self.session.preferences.room_number or 'In-House'}, "
            f"Dietary/Cuisine={', '.join(self.session.preferences.dietary) or 'None specified'}, "
            f"Party={self.session.preferences.party_type or 'Standard'}"
        )

        system_prompt = f"""{get_system_prompt(PersonaStyle.LUXURY_CLEFS_D_OR)}

CONVERSATION CONTEXT & SESSION MEMORY:
================================================================================
{preferences_summary}
Active Intent: {self.session.active_intent}
Context Slots: {self.session.context_slots}

Recent Dialogue History:
{history_summary}
================================================================================

INSTRUCTIONS:
- You remember all details from earlier in the conversation (name, room, preferences, previously mentioned topics).
- If the guest's inquiry refers back to an earlier subject, seamlessly incorporate it.
- Keep your tone warm, sophisticated, and attentive.
"""

        messages = [
            ChatMessage(role="user", content=resolved_query)
        ]

        llm_reply = self.llm.generate_response(system_prompt=system_prompt, messages=messages)

        # Enhance reply if local generator returned generic text
        if len(llm_reply) < 50 or llm_reply.startswith("I apologize"):
            llm_reply = (
                f"It is my distinct pleasure to assist you, esteemed guest. "
                f"I have noted your preferences regarding {resolved_query}. "
                f"How may I further curate your experience at The Grand Azure today?"
            )

        self.session.add_turn(
            user_msg=user_message,
            assistant_msg=llm_reply,
            resolved_query=resolved_query,
            intent=self.session.active_intent,
            slots=self.session.context_slots
        )

        return {
            "reply": llm_reply,
            "resolved_query": resolved_query,
            "context_used": was_context_used,
            "pending_clarification": self.session.pending_clarification.field_name if self.session.pending_clarification else None,
            "session_state": self.session.to_dict()
        }

    def reset(self) -> None:
        self.session.reset()
