"""Module 3: Embedding-based Guest Query Intent Classifier

Uses vector embeddings and semantic cosine similarity against reference
exemplars in ChromaDB to classify intent, domain, and urgency.
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions

from src.module3_classifier.schemas import (
    IntentCategory,
    DomainCategory,
    UrgencyLevel,
    ClassificationResult,
    ExtractedEntities
)


# Curated reference exemplars across categories & domains
INTENT_EXEMPLARS = [
    # Information
    {
        "text": "What time does breakfast start in the morning?",
        "intent": IntentCategory.INFORMATION.value,
        "domain": DomainCategory.DINING.value,
        "urgency": UrgencyLevel.LOW.value,
        "routing": "Dining Information / RAG"
    },
    {
        "text": "What are your check-in and check-out times?",
        "intent": IntentCategory.INFORMATION.value,
        "domain": DomainCategory.FRONT_DESK.value,
        "urgency": UrgencyLevel.LOW.value,
        "routing": "Front Desk Policy / RAG"
    },
    {
        "text": "Is the swimming pool heated and what are the opening hours?",
        "intent": IntentCategory.INFORMATION.value,
        "domain": DomainCategory.AMENITIES.value,
        "urgency": UrgencyLevel.LOW.value,
        "routing": "Amenities / RAG"
    },
    {
        "text": "What is the cancellation policy for suites?",
        "intent": IntentCategory.INFORMATION.value,
        "domain": DomainCategory.FRONT_DESK.value,
        "urgency": UrgencyLevel.LOW.value,
        "routing": "Front Desk Policy / RAG"
    },
    {
        "text": "Do you have high speed internet and wifi in the bedroom?",
        "intent": IntentCategory.INFORMATION.value,
        "domain": DomainCategory.ROOMS.value,
        "urgency": UrgencyLevel.LOW.value,
        "routing": "Room Amenities / RAG"
    },

    # Recommendation
    {
        "text": "Can you recommend a romantic seafood restaurant nearby with sunset views?",
        "intent": IntentCategory.RECOMMENDATION.value,
        "domain": DomainCategory.DINING.value,
        "urgency": UrgencyLevel.LOW.value,
        "routing": "Concierge Dining Advisor"
    },
    {
        "text": "What are some fun family activities or sights to visit around here?",
        "intent": IntentCategory.RECOMMENDATION.value,
        "domain": DomainCategory.ATTRACTIONS.value,
        "urgency": UrgencyLevel.LOW.value,
        "routing": "Local Sightseeing Advisor"
    },
    {
        "text": "What is the best spa massage treatment for chronic back pain?",
        "intent": IntentCategory.RECOMMENDATION.value,
        "domain": DomainCategory.SPA_WELLNESS.value,
        "urgency": UrgencyLevel.LOW.value,
        "routing": "Spa Wellness Advisor"
    },
    {
        "text": "Where should we go hiking or exploring nature trails?",
        "intent": IntentCategory.RECOMMENDATION.value,
        "domain": DomainCategory.ATTRACTIONS.value,
        "urgency": UrgencyLevel.LOW.value,
        "routing": "Outdoor Activities Advisor"
    },

    # Action-Based
    {
        "text": "I need extra towels, pillows and shampoo brought to my room.",
        "intent": IntentCategory.ACTION_BASED.value,
        "domain": DomainCategory.HOUSEKEEPING.value,
        "urgency": UrgencyLevel.HIGH.value,
        "routing": "Housekeeping Dispatch Workflow"
    },
    {
        "text": "Please book a table for 4 at Le Jardin Bistro tonight at 8 PM.",
        "intent": IntentCategory.ACTION_BASED.value,
        "domain": DomainCategory.DINING.value,
        "urgency": UrgencyLevel.MEDIUM.value,
        "routing": "Restaurant Reservation Service"
    },
    {
        "text": "Can you schedule an executive airport transfer for tomorrow morning at 7 AM?",
        "intent": IntentCategory.ACTION_BASED.value,
        "domain": DomainCategory.TRANSPORTATION.value,
        "urgency": UrgencyLevel.MEDIUM.value,
        "routing": "Transportation Booking Workflow"
    },
    {
        "text": "I would like to order room service breakfast to room 305.",
        "intent": IntentCategory.ACTION_BASED.value,
        "domain": DomainCategory.DINING.value,
        "urgency": UrgencyLevel.HIGH.value,
        "routing": "In-Room Dining POS"
    },

    # Complaint
    {
        "text": "The air conditioning in my room is broken and making loud noises.",
        "intent": IntentCategory.COMPLAINT.value,
        "domain": DomainCategory.MAINTENANCE.value,
        "urgency": UrgencyLevel.HIGH.value,
        "routing": "Maintenance Priority Escalation"
    },
    {
        "text": "There is an incorrect duplicate charge on my folio bill.",
        "intent": IntentCategory.COMPLAINT.value,
        "domain": DomainCategory.BILLING.value,
        "urgency": UrgencyLevel.MEDIUM.value,
        "routing": "Front Desk Folio Audit"
    },

    # Emergency
    {
        "text": "Help, my friend collapsed in the lobby and needs an ambulance!",
        "intent": IntentCategory.EMERGENCY.value,
        "domain": DomainCategory.FRONT_DESK.value,
        "urgency": UrgencyLevel.CRITICAL.value,
        "routing": "Emergency Response & MOD Alert"
    }
]


class EmbeddingIntentClassifier:
    """Classifies queries using vector similarity against reference exemplars."""

    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name="intent_exemplars",
            metadata={"description": "Exemplars for guest query intent classification"}
        )
        self._seed_exemplars()

    def _seed_exemplars(self):
        # Check if already seeded
        if self.collection.count() > 0:
            return

        documents = [ex["text"] for ex in INTENT_EXEMPLARS]
        metadatas = [
            {
                "intent": ex["intent"],
                "domain": ex["domain"],
                "urgency": ex["urgency"],
                "routing": ex["routing"]
            }
            for ex in INTENT_EXEMPLARS
        ]
        ids = [f"ex_{i}" for i in range(len(INTENT_EXEMPLARS))]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def classify(self, query: str) -> ClassificationResult:
        """Finds closest exemplars and derives classification."""
        results = self.collection.query(
            query_texts=[query],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )

        top_meta = results["metadatas"][0][0]
        distance = results["distances"][0][0] if "distances" in results and results["distances"] else 0.5
        # Convert distance to approximate cosine similarity confidence: 1 / (1 + distance)
        confidence = max(0.5, min(0.98, round(1.0 / (1.0 + float(distance)), 2)))

        matched_doc = results["documents"][0][0]
        reasoning = f"Matched nearest exemplar: '{matched_doc}' (similarity: {confidence:.2f})"

        # Simple entity extraction heuristic
        entities = self._extract_entities_heuristic(query)

        return ClassificationResult(
            query=query,
            intent_category=IntentCategory(top_meta["intent"]),
            domain=DomainCategory(top_meta["domain"]),
            urgency=UrgencyLevel(top_meta["urgency"]),
            confidence=confidence,
            entities=entities,
            reasoning=reasoning,
            recommended_routing=top_meta["routing"]
        )

    def _extract_entities_heuristic(self, query: str) -> ExtractedEntities:
        import re
        q = query.lower()
        entities = ExtractedEntities()

        # Room match (e.g. room 412, room 305, villa 3)
        room_match = re.search(r'\b(?:room|villa|suite)\s+([0-9a-zA-Z]+)\b', q)
        if room_match:
            entities.room_number = room_match.group(1).upper()

        # Party size match
        party_match = re.search(r'\b(?:for|party of)\s+(\d+)\b', q)
        if party_match:
            entities.party_size = int(party_match.group(1))

        # Time match
        time_match = re.search(r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm))\b', q)
        if time_match:
            entities.target_time = time_match.group(1).upper()

        # Items
        items = []
        for item in ["towel", "towels", "water", "pillow", "pillows", "shampoo", "blanket", "iron", "ice"]:
            if item in q:
                items.append(item)
        entities.requested_items = items

        return entities
