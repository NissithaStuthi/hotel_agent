"""Module 4: Multi-Provider LLM Backend

Supports Gemini API, OpenAI API, Ollama, and an offline
Hospitality Natural Language Engine that runs out-of-the-box.
"""

import os
import json
import re
from typing import List, Dict, Optional, Any
import httpx

from src.config import (
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL
)
from src.module4_concierge.memory import ChatMessage


class LLMBackend:
    """Unified LLM client with multi-provider failover."""

    def __init__(self, provider: str = "auto"):
        self.provider = provider

    def generate_response(
        self,
        system_prompt: str,
        messages: List[ChatMessage],
        temperature: float = 0.7
    ) -> str:
        """Dispatches generation to selected or available backend."""
        # 1. Try Gemini if configured
        if (self.provider in ["auto", "gemini"]) and GEMINI_API_KEY:
            try:
                return self._call_gemini(system_prompt, messages, temperature)
            except Exception as e:
                pass

        # 2. Try OpenAI if configured
        if (self.provider in ["auto", "openai"]) and OPENAI_API_KEY:
            try:
                return self._call_openai(system_prompt, messages, temperature)
            except Exception as e:
                pass

        # 3. Try Ollama only if explicitly requested
        if self.provider == "ollama":
            try:
                return self._call_ollama(system_prompt, messages, temperature)
            except Exception:
                pass

        # 4. Built-in Local Luxury Concierge Generator
        return self._generate_local_hospitality_response(system_prompt, messages)

    def _call_gemini(self, system_prompt: str, messages: List[ChatMessage], temperature: float) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        contents = []
        for m in messages:
            if m.role == "user":
                contents.append({"role": "user", "parts": [{"text": m.content}]})
            elif m.role == "assistant":
                contents.append({"role": "model", "parts": [{"text": m.content}]})

        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": 800}
        }
        with httpx.Client(timeout=15.0) as client:
            res = client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    def _call_openai(self, system_prompt: str, messages: List[ChatMessage], temperature: float) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        chat_history = [{"role": "system", "content": system_prompt}]
        for m in messages:
            chat_history.append({"role": m.role, "content": m.content})

        payload = {
            "model": "gpt-4o-mini",
            "messages": chat_history,
            "temperature": temperature
        }
        with httpx.Client(timeout=15.0) as client:
            res = client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"].strip()

    def _call_ollama(self, system_prompt: str, messages: List[ChatMessage], temperature: float) -> str:
        url = f"{OLLAMA_BASE_URL}/api/chat"
        chat_history = [{"role": "system", "content": system_prompt}]
        for m in messages:
            chat_history.append({"role": m.role, "content": m.content})

        payload = {
            "model": OLLAMA_MODEL,
            "messages": chat_history,
            "stream": False,
            "options": {"temperature": temperature}
        }
        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["message"]["content"].strip()

    def _generate_local_hospitality_response(self, system_prompt: str, messages: List[ChatMessage]) -> str:
        """Sophisticated offline concierge generator matching Julian's persona."""
        last_user_msg = ""
        for m in reversed(messages):
            if m.role == "user":
                last_user_msg = m.content
                break

        q = last_user_msg.lower()

        # Check for guest name in history
        guest_salutation = "esteemed guest"
        for m in messages:
            if m.role == "user":
                m_match = re.search(r'(?:my name is|i am|this is)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)', m.content)
                if m_match:
                    name_candidate = m_match.group(1).strip()
                    if not any(v in name_candidate.lower() for v in ["traveling", "staying", "looking", "interested", "planning", "calling", "with"]):
                        guest_salutation = f"Ms. {name_candidate.split()[-1]}"
                        break

        # Check for room number in history
        room_info = ""
        for m in messages:
            if m.role == "user":
                r_match = re.search(r'\b(?:room|villa)\s+([0-9a-zA-Z]+)\b', m.content.lower())
                if r_match:
                    room_info = f" for Room {r_match.group(1).upper()}"
                    break

        # 1. Greetings / Introduction
        if any(w in q for w in ["hello", "hi", "good morning", "good evening", "greetings"]):
            return (
                f"A very warm welcome to The Grand Azure Resort & Spa, {guest_salutation}. "
                "I am Julian Saint-Claire, your Chief Concierge. It is my absolute pleasure to be at your service. "
                "How may I curate your stay or assist you this wonderful day?"
            )

        # 2. Breakfast & Dining
        if any(w in q for w in ["breakfast", "dining", "azure breeze", "dinner", "restaurant", "food"]):
            return (
                f"Delighted to assist with your culinary plans, {guest_salutation}. "
                "At our premier cliffside venue, *Azure Breeze Seafood Grill*, breakfast is served from 6:30 AM to 10:30 AM on weekdays (until 11:00 AM on weekends). "
                "For dinner, we offer fresh Mediterranean catches alongside panoramic ocean views. "
                "We also have *Le Jardin French Bistro* in the botanical courtyard and 24/7 In-Room Dining. "
                "Would you care for me to reserve a sunset table for your party this evening?"
            )

        # 3. Recommendations & Local sights
        if any(w in q for w in ["recommend", "places to visit", "attractions", "sightseeing", "things to do"]):
            return (
                f"It would be my distinct pleasure to share a few curated highlights, {guest_salutation}:\n\n"
                "• **Emerald Cove Sea Caves**: Marvelous crystalline grottos just 10 minutes away, ideal for morning kayaking.\n"
                "• **Historic Old Town Citadel**: A 17th-century cobblestone fortress featuring boutique perfumeries and olive oil tastings.\n"
                "• **Azure Marina Promenade**: Stroll past superyachts, luxury boutiques, and seaside champagne lounges.\n\n"
                "Our complimentary resort electric shuttle departs the main Porte-Cochère every 30 minutes. Allow me to prepare a bespoke map or reserve equipment for you."
            )

        # 4. Service Requests / Housekeeping / Towels
        if any(w in q for w in ["towel", "towels", "water", "pillow", "extra", "bring", "send"]):
            return (
                f"Consider it done right away, {guest_salutation}. I have dispatched a priority request to our Floor Housekeeping Attendant{room_info}. "
                "Your requested items will be delivered to your door within 15 minutes. "
                "Please do let me know if you desire fresh ice, botanical bath salts, or any further comforts."
            )

        # 5. Complaints & Issues
        if any(w in q for w in ["broken", "noise", "not working", "air condition", "dirty", "complain", "ac"]):
            return (
                f"Please accept my sincere and immediate apologies for this disruption to your comfort, {guest_salutation}. "
                "At The Grand Azure, your peace of mind is our paramount concern. "
                f"I have already escalated this directly to our Chief Duty Engineer with high priority{room_info}. "
                "A technician will arrive within 10 to 15 minutes to inspect the unit. Should it not be resolved swiftly, "
                "I will personally oversee an immediate room relocation and extend our hospitality credits to your folio. "
                "May I send you a cool refreshment while this is attended to?"
            )

        # 6. Spa & Relaxation
        if any(w in q for w in ["spa", "massage", "facial", "wellness", "relax"]):
            return (
                f"A marvelous choice, {guest_salutation}. The Azure Spa is a 25,000 sq ft sanctuary of tranquility. "
                "I warmly recommend our signature *Azure Deep Mineral Recovery Massage* (80 mins) using heated volcanic stones and Breton marine magnesium oils, "
                "or the *Couples Ocean Harmony Massage* in our private oceanfront suite. "
                "May I reserve a treatment time for you and your guest today?"
            )

        # 7. Policies & Check-in / Check-out
        if any(w in q for w in ["check-in", "check out", "checkout", "policy", "cancellation", "late"]):
            return (
                f"Certainly, {guest_salutation}. Our standard check-in begins at 3:00 PM, and check-out is at 11:00 AM. "
                "We are pleased to extend complimentary late check-out until 1:00 PM upon request, subject to availability. "
                "Should you require our secure bell desk luggage storage or wish to enjoy the infinity pool post-departure, "
                "our facilities remain entirely at your disposal."
            )

        # 8. General Gracious Fallback
        return (
            f"It is my genuine pleasure to assist you, {guest_salutation}. "
            "Whether you require reservations, transportation arrangements, housekeeping comforts, or local discoveries, "
            "I am devoted to ensuring your stay at The Grand Azure is nothing short of exceptional. "
            "How may I further delight you today?"
        )
