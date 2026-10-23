"""Module 3: LLM & Semantic Rule Classifier with Structured Output"""

import os
import json
import re
from typing import Optional
from src.config import GEMINI_API_KEY, OPENAI_API_KEY
from src.module3_classifier.schemas import (
    IntentCategory,
    DomainCategory,
    UrgencyLevel,
    ClassificationResult,
    ExtractedEntities
)


class LLMIntentClassifier:
    """Classifies guest queries using LLM or robust fallback semantic parser."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY or OPENAI_API_KEY

    def classify(self, query: str) -> ClassificationResult:
        """Attempts LLM structured output, falling back to rule-based semantic parser."""
        if self.api_key:
            try:
                return self._classify_via_api(query)
            except Exception as e:
                # Fallback on API failure
                pass
        return self._classify_via_rule_heuristics(query)

    def _classify_via_api(self, query: str) -> ClassificationResult:
        import httpx
        # If Gemini Key available, invoke Gemini REST API
        if GEMINI_API_KEY:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            prompt = f"""You are an expert hotel query intent classifier.
Analyze this guest query: "{query}"

Output ONLY a raw JSON object adhering to this schema:
{{
  "intent_category": "Information" | "Recommendation" | "Action-Based" | "Complaint & Feedback" | "Emergency & Escalation",
  "domain": "Front Desk & Policies" | "Rooms & Accommodation" | "Restaurants & Room Service" | "Spa & Wellness" | "Hotel Facilities & Amenities" | "Local Attractions & Sightseeing" | "Transportation & Valet" | "Housekeeping & Supplies" | "Maintenance & Engineering" | "Billing & Payments",
  "urgency": "Low" | "Medium" | "High" | "Critical",
  "confidence": 0.95,
  "room_number": null or string,
  "party_size": null or integer,
  "target_time": null or string,
  "requested_items": [],
  "reasoning": "short explanation",
  "recommended_routing": "target department"
}}
"""
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload)
                data = res.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Clean JSON fences
                cleaned = re.sub(r"```json|```", "", raw_text).strip()
                parsed = json.loads(cleaned)

                entities = ExtractedEntities(
                    room_number=parsed.get("room_number"),
                    party_size=parsed.get("party_size"),
                    target_time=parsed.get("target_time"),
                    requested_items=parsed.get("requested_items", [])
                )
                return ClassificationResult(
                    query=query,
                    intent_category=IntentCategory(parsed["intent_category"]),
                    domain=DomainCategory(parsed["domain"]),
                    urgency=UrgencyLevel(parsed["urgency"]),
                    confidence=float(parsed.get("confidence", 0.9)),
                    entities=entities,
                    reasoning=parsed.get("reasoning", "LLM classified"),
                    recommended_routing=parsed.get("recommended_routing", "General Concierge")
                )

        raise RuntimeError("No active API response")

    def _classify_via_rule_heuristics(self, query: str) -> ClassificationResult:
        """Deterministic semantic fallback parser."""
        q = query.lower()

        # 1. Emergency detection
        if any(w in q for w in ["help", "ambulance", "hurt", "collapsed", "bleeding", "fire", "emergency", "police"]):
            return ClassificationResult(
                query=query,
                intent_category=IntentCategory.EMERGENCY,
                domain=DomainCategory.FRONT_DESK,
                urgency=UrgencyLevel.CRITICAL,
                confidence=0.98,
                reasoning="Safety/emergency keywords detected requiring immediate escalation",
                recommended_routing="Emergency Response & MOD Alert"
            )

        # 2. Complaint detection
        if any(w in q for w in ["broken", "not working", "dirty", "loud", "noise", "charged twice", "terrible", "complaint", "leaking", "stain", "rude"]):
            domain = DomainCategory.MAINTENANCE
            if any(w in q for w in ["charge", "charged", "folio", "bill", "invoice", "double"]):
                domain = DomainCategory.BILLING
            return ClassificationResult(
                query=query,
                intent_category=IntentCategory.COMPLAINT,
                domain=domain,
                urgency=UrgencyLevel.HIGH if "not working" in q or "broken" in q else UrgencyLevel.MEDIUM,
                confidence=0.92,
                reasoning="Service dissatisfaction or issue report identified",
                recommended_routing="Guest Relations De-escalation"
            )

        # 3. Action-based requests
        action_verbs = ["book", "reserve", "send", "bring", "i need", "order", "call a cab", "schedule", "can i get", "have sent"]
        if any(w in q for w in action_verbs):
            if any(w in q for w in ["towel", "water", "pillow", "shampoo", "blanket", "iron", "crib"]):
                domain = DomainCategory.HOUSEKEEPING
                routing = "Housekeeping Dispatch Workflow"
                urgency = UrgencyLevel.HIGH
            elif any(w in q for w in ["table", "dinner", "lunch", "restaurant", "bistro", "room service"]):
                domain = DomainCategory.DINING
                routing = "Dining Reservation / Room Service Dispatch"
                urgency = UrgencyLevel.MEDIUM
            elif any(w in q for w in ["transfer", "taxi", "cab", "airport", "car rental", "chauffeur"]):
                domain = DomainCategory.TRANSPORTATION
                routing = "Valet & Transportation Workflow"
                urgency = UrgencyLevel.MEDIUM
            elif any(w in q for w in ["massage", "facial", "spa", "treatment"]):
                domain = DomainCategory.SPA_WELLNESS
                routing = "Spa Booking Service"
                urgency = UrgencyLevel.MEDIUM
            else:
                domain = DomainCategory.FRONT_DESK
                routing = "Front Desk Guest Services"
                urgency = UrgencyLevel.MEDIUM

            # Entities
            entities = ExtractedEntities()
            room_match = re.search(r'\b(?:room|villa|suite)\s+([0-9a-zA-Z]+)\b', q)
            if room_match:
                entities.room_number = room_match.group(1).upper()
            party_match = re.search(r'\b(?:for|party of)\s+(\d+)\b', q)
            if party_match:
                entities.party_size = int(party_match.group(1))
            items = []
            for item in ["towel", "towels", "water", "pillow", "pillows", "shampoo", "blanket", "iron", "ice", "crib"]:
                if re.search(rf"\b{item}\b", q):
                    items.append(item)
            entities.requested_items = items

            return ClassificationResult(
                query=query,
                intent_category=IntentCategory.ACTION_BASED,
                domain=domain,
                urgency=urgency,
                confidence=0.91,
                entities=entities,
                reasoning="Action request pattern detected with actionable service requirements",
                recommended_routing=routing
            )

        # 4. Recommendation requests
        if any(w in q for w in ["recommend", "suggest", "where should", "what should", "best place", "ideas", "good spots"]):
            if any(w in q for w in ["spa", "massage", "facial", "relax", "wellness"]):
                domain = DomainCategory.SPA_WELLNESS
                routing = "Spa Wellness Advisor"
            elif any(re.search(rf"\b{w}\b", q) for w in ["eat", "restaurant", "dinner", "seafood", "lunch", "drink", "cocktail", "food"]):
                domain = DomainCategory.DINING
                routing = "Concierge Dining Advisor"
            else:
                domain = DomainCategory.ATTRACTIONS
                routing = "Local Sightseeing Advisor"

            return ClassificationResult(
                query=query,
                intent_category=IntentCategory.RECOMMENDATION,
                domain=domain,
                urgency=UrgencyLevel.LOW,
                confidence=0.90,
                reasoning="Guest seeking advisory recommendation or curated options",
                recommended_routing=routing
            )

        # 5. Default to Information
        domain = DomainCategory.FRONT_DESK
        if any(w in q for w in ["breakfast", "dinner", "menu", "restaurant", "eat", "food"]):
            domain = DomainCategory.DINING
        elif any(w in q for w in ["pool", "gym", "fitness", "beach", "cabana", "parking", "valet"]):
            domain = DomainCategory.AMENITIES
        elif any(w in q for w in ["spa", "sauna", "massage"]):
            domain = DomainCategory.SPA_WELLNESS
        elif any(w in q for w in ["room", "suite", "bed", "balcony", "view", "wifi"]):
            domain = DomainCategory.ROOMS
        elif any(w in q for w in ["shuttle", "airport", "uber", "car", "distance"]):
            domain = DomainCategory.TRANSPORTATION

        return ClassificationResult(
            query=query,
            intent_category=IntentCategory.INFORMATION,
            domain=domain,
            urgency=UrgencyLevel.LOW,
            confidence=0.88,
            reasoning="Inquiry seeking factual knowledge, hours, or hotel policies",
            recommended_routing="Hotel Knowledge RAG Engine"
        )
