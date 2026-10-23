"""Module 8: Short-Term Context Resolver & Coreference Resolution

Resolves incomplete, elided, or anaphoric guest responses using conversation memory,
active session state, and pending question context.
"""

import re
from typing import Tuple, Dict, Any, Optional
from src.module8_context_memory.session_state import SessionState, PendingClarification


class ShortTermContextResolver:
    """Resolves short follow-up messages into fully grounded contextual queries."""

    CUISINE_KEYWORDS = [
        "italian", "french", "seafood", "mediterranean", "japanese", "sushi",
        "steakhouse", "american", "mexican", "asian", "tapas", "vegetarian", "vegan"
    ]

    TIME_PATTERNS = [
        r'\b(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b',
        r'\b(tonight|tomorrow|tomorrow night|this evening|morning|afternoon)\b',
        r'\b(around\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b'
    ]

    PARTY_PATTERNS = [
        r'\b(?:for\s+)?(\d+)\s*(?:people|persons|guests|of us|adults)\b',
        r'\b(just\s+(?:me|myself|two of us|three of us|four of us))\b',
        r'\b(table for\s+\d+)\b'
    ]

    def resolve(self, raw_message: str, session: SessionState) -> Tuple[str, Dict[str, Any], bool]:
        """Resolves raw guest input into (resolved_query, updated_slots, was_context_used)."""
        clean_msg = raw_message.strip()
        lower_msg = clean_msg.lower()
        new_slots: Dict[str, Any] = {}
        was_context_used = False

        # 1. Check if guest is answering a pending clarification question
        if session.pending_clarification:
            pending = session.pending_clarification
            
            # Case A: Pending cuisine preference (e.g. "What type of food do you prefer?")
            if pending.field_name == "cuisine":
                cuisine_found = None
                for c in self.CUISINE_KEYWORDS:
                    if c in lower_msg:
                        cuisine_found = c.title()
                        break
                
                if cuisine_found or len(clean_msg.split()) <= 4:
                    cuisine_val = cuisine_found or clean_msg.title()
                    session.update_slot("cuisine", cuisine_val)
                    new_slots["cuisine"] = cuisine_val
                    
                    if cuisine_val not in session.preferences.dietary:
                        session.preferences.dietary.append(cuisine_val)

                    meal = session.get_slot("meal", "dinner")
                    resolved_query = f"Recommend a fine {cuisine_val} restaurant for {meal}."
                    session.clear_pending_clarification()
                    return resolved_query, new_slots, True

            # Case B: Pending party size
            elif pending.field_name == "party_size":
                party_match = re.search(r'\b(\d+)\b', lower_msg)
                if party_match:
                    size = int(party_match.group(1))
                    session.update_slot("party_size", size)
                    new_slots["party_size"] = size
                    resolved_query = f"Table reservation for {size} guests at {session.get_slot('target_venue', 'the restaurant')}."
                    session.clear_pending_clarification()
                    return resolved_query, new_slots, True

            # Case C: Pending time
            elif pending.field_name == "time":
                session.update_slot("reservation_time", clean_msg)
                new_slots["reservation_time"] = clean_msg
                resolved_query = f"Reservation at {clean_msg} for {session.get_slot('target_venue', 'the restaurant')}."
                session.clear_pending_clarification()
                return resolved_query, new_slots, True

        # 2. Check for isolated cuisine keyword in active restaurant context
        if session.active_intent in ["dining_recommendation", "restaurant_inquiry", "dinner_request"]:
            for c in self.CUISINE_KEYWORDS:
                if c in lower_msg and len(lower_msg.split()) <= 3:
                    cuisine_val = c.title()
                    session.update_slot("cuisine", cuisine_val)
                    new_slots["cuisine"] = cuisine_val
                    if cuisine_val not in session.preferences.dietary:
                        session.preferences.dietary.append(cuisine_val)
                    meal = session.get_slot("meal", "dinner")
                    resolved_query = f"Recommend an exquisite {cuisine_val} restaurant for {meal}."
                    return resolved_query, new_slots, True

        # 3. Check for coreferent pronouns ("it", "there", "that restaurant", "the pool", "that place")
        coref_triggers = ["how far is it", "what are the hours there", "is it open", "can you book it", "how much is it", "what is the dress code there"]
        if any(tr in lower_msg for tr in coref_triggers):
            target = session.get_slot("target_venue") or session.get_slot("last_mentioned_entity") or "the venue"
            resolved_query = f"{clean_msg} (referring specifically to {target})"
            return resolved_query, new_slots, True

        # 4. Extract implicit preferences & slot attributes
        self._extract_entities_and_preferences(clean_msg, session, new_slots)

        # 5. New or independent query
        # Detect new intent
        if any(w in lower_msg for w in ["restaurant", "dinner", "lunch", "eat", "dining"]):
            session.active_intent = "dining_recommendation"
            session.active_domain = "dining"
            if "dinner" in lower_msg:
                session.update_slot("meal", "dinner")
            elif "lunch" in lower_msg:
                session.update_slot("meal", "lunch")
        elif any(w in lower_msg for w in ["housekeeping", "towel", "pillow", "clean"]):
            session.active_intent = "housekeeping_request"
            session.active_domain = "housekeeping"
        elif any(w in lower_msg for w in ["spa", "massage", "facial"]):
            session.active_intent = "spa_inquiry"
            session.active_domain = "spa"

        return clean_msg, new_slots, False

    def _extract_entities_and_preferences(
        self,
        text: str,
        session: SessionState,
        slots: Dict[str, Any]
    ) -> None:
        """Extracts name, room number, children/family status, dietary restrictions."""
        lower = text.lower()

        # Children / Family
        if any(w in lower for w in ["with children", "with kids", "with my children", "with toddlers", "family of"]):
            session.preferences.party_type = "family_with_children"
            slots["party_type"] = "family_with_children"

        # Couple / Romantic
        if any(w in lower for w in ["anniversary", "honeymoon", "romantic", "my wife and i", "my husband and i", "my partner"]):
            if "anniversary" in lower and "Anniversary" not in session.preferences.special_occasions:
                session.preferences.special_occasions.append("Anniversary")
            if not session.preferences.party_type:
                session.preferences.party_type = "couple_romantic"
            slots["party_type"] = "couple_romantic"

        # Dietary
        if "vegetarian" in lower and "Vegetarian" not in session.preferences.dietary:
            session.preferences.dietary.append("Vegetarian")
        if "gluten-free" in lower and "Gluten-Free" not in session.preferences.dietary:
            session.preferences.dietary.append("Gluten-Free")

        # Room number
        room_match = re.search(r'\b(?:room|suite|villa)\s+([0-9a-zA-Z]+)\b', lower)
        if room_match:
            r_num = room_match.group(1).upper()
            session.preferences.room_number = r_num
            slots["room_number"] = r_num

        # Name
        name_match = re.search(r'(?:my name is|i am|this is)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)', text, re.IGNORECASE)
        if name_match:
            guest_n = name_match.group(1).strip()
            # Clean up trailing words like 'staying' if captured
            for noise in ["Staying", "In", "From", "At"]:
                if guest_n.endswith(f" {noise}"):
                    guest_n = guest_n[:-len(noise)-1].strip()
            session.preferences.guest_name = guest_n
            slots["guest_name"] = guest_n
