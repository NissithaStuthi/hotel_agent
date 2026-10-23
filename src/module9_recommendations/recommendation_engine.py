"""Module 9: Personalized Recommendation Engine

Combines vector embeddings, multi-criteria constraint scoring (family alignment,
distance proximity, operating hours), and LLM reasoning to curate tailored recommendations.
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import chromadb

from src.config import CHROMA_PERSIST_DIR
from src.module9_recommendations.models import (
    GuestProfile,
    RecommendationCandidate,
    ScoredRecommendation,
    RecommendationResponse
)
from src.module9_recommendations.preference_extractor import PreferenceExtractor
from src.module4_concierge.persona import PersonaStyle, get_system_prompt
from src.module4_concierge.llm_backend import LLMBackend
from src.module4_concierge.memory import ChatMessage


class PersonalizedRecommendationEngine:
    """Multi-criteria personalized recommendation engine with LLM reasoning."""

    def __init__(
        self,
        persist_dir: Path = CHROMA_PERSIST_DIR,
        provider: str = "auto"
    ):
        self.extractor = PreferenceExtractor()
        self.llm = LLMBackend(provider=provider)
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name="personalized_recommendation_candidates",
            metadata={"hnsw:space": "cosine"}
        )
        self.candidates: List[RecommendationCandidate] = []
        self._init_candidates_catalog()

    def _init_candidates_catalog(self) -> None:
        """Loads and indexes candidates spanning resort amenities and local attractions."""
        catalog_raw = [
            {
                "id": "REC-KIDS-01",
                "name": "Little Mariners Kids Club & Marine Adventure",
                "category": "Family & Children",
                "location_type": "resort",
                "distance_km": 0.0,
                "travel_time_minutes": 0,
                "operating_hours": "9:00 AM - 5:00 PM Daily",
                "family_friendly": True,
                "min_age": 4,
                "price_level": "Complimentary",
                "tags": ["family", "children", "kids_club", "indoor_outdoor", "supervised", "crafts", "on_site"],
                "description": "Complimentary supervised marine activities, treasure hunts, coastal craft ateliers, and marine biology workshops for children aged 4 to 12. Evening pajama movie parties on weekends.",
                "insider_tips": "Book the 2:00 PM Sea Turtle Ecology session—kids receive an honorary Junior Marine Ranger badge."
            },
            {
                "id": "REC-POOL-FAMILY",
                "name": "Family Splash Lagoon & Kids Zero-Entry Pool",
                "category": "Recreation & Pool",
                "location_type": "resort",
                "distance_km": 0.0,
                "travel_time_minutes": 0,
                "operating_hours": "9:00 AM - 7:00 PM Daily",
                "family_friendly": True,
                "min_age": 0,
                "price_level": "Complimentary",
                "tags": ["family", "children", "pool", "water_play", "heated", "on_site"],
                "description": "Heated to 84°F with gentle zero-entry beach slopes, playful bubbling fountains, and certified lifeguards on duty. Complimentary swim vests and water toys provided.",
                "insider_tips": "Poolside attendants offer complimentary fruit skewers and smoothies at 11:30 AM and 3:30 PM."
            },
            {
                "id": "REC-KAYAK-01",
                "name": "Emerald Cove Sea Caves & Family Tandem Kayaking",
                "category": "Nature & Adventure",
                "location_type": "nearby_destination",
                "distance_km": 3.2,
                "travel_time_minutes": 10,
                "operating_hours": "9:00 AM - 5:00 PM Daily",
                "family_friendly": True,
                "min_age": 6,
                "price_level": "$$",
                "tags": ["nature", "water_sports", "family", "scenic", "kayak", "nearby"],
                "description": "Crystalline, tranquil sea caves with gentle waters ideal for family tandem sea kayaking. Guided eco-tours explore glowing grottoes and secluded pebble beaches.",
                "insider_tips": "Morning departures at 9:30 AM have the calmest seas and softest sunlight for children."
            },
            {
                "id": "REC-MARINA-01",
                "name": "Azure Marina Waterfront Promenade & Artisan Gelato",
                "category": "Leisure & Dining",
                "location_type": "nearby_destination",
                "distance_km": 1.5,
                "travel_time_minutes": 5,
                "operating_hours": "10:00 AM - 10:00 PM Daily",
                "family_friendly": True,
                "min_age": 0,
                "price_level": "$$",
                "tags": ["walkable", "gelato", "family", "shopping", "promenade", "dining", "nearby"],
                "description": "Pedestrian-only seaside promenade with artisan Italian gelaterias, yachts, maritime boutiques, and scenic sunset boardwalk.",
                "insider_tips": "Board our complimentary resort Mercedes shuttle at the Porte-Cochère; runs every 30 minutes."
            },
            {
                "id": "REC-GARDEN-01",
                "name": "Monte Azure Cliffside Botanical Gardens",
                "category": "Nature & Sightseeing",
                "location_type": "nearby_destination",
                "distance_km": 5.0,
                "travel_time_minutes": 12,
                "operating_hours": "9:00 AM - 6:00 PM Daily",
                "family_friendly": True,
                "min_age": 0,
                "price_level": "$",
                "tags": ["nature", "scenic", "family", "walking", "gardens", "cliff_views"],
                "description": "15-acre terraced subtropical oasis with exotic succulents, shaded pine pergolas, and breathtaking 180-degree Mediterranean vistas.",
                "insider_tips": "Stroller-friendly paved pathways loop through the lower garden levels."
            },
            {
                "id": "REC-OLDTOWN-01",
                "name": "Historic Old Town Citadel & Artisan Craft Quarter",
                "category": "History & Culture",
                "location_type": "nearby_destination",
                "distance_km": 7.5,
                "travel_time_minutes": 18,
                "operating_hours": "10:00 AM - 7:00 PM Daily",
                "family_friendly": True,
                "min_age": 0,
                "price_level": "$$",
                "tags": ["culture", "history", "artisan", "shopping", "walks"],
                "description": "17th-century fortress citadel with cobblestone pathways, bespoke perfume ateliers, ceramic workshops, and charming open-air cafes.",
                "insider_tips": "Visit Rue des Oliviers for fresh olive oil tastings and handmade lavender sachets."
            },
            {
                "id": "REC-POOL-SERENITY",
                "name": "The Serenity Adults-Only Pool & Cabanas",
                "category": "Adults Relaxation",
                "location_type": "resort",
                "distance_km": 0.0,
                "travel_time_minutes": 0,
                "operating_hours": "8:00 AM - 8:00 PM Daily",
                "family_friendly": False,
                "min_age": 18,
                "price_level": "$$$",
                "tags": ["adults_only", "quiet", "pool", "cocktails", "luxury", "on_site"],
                "description": "Heated 84°F saltwater infinity pool strictly reserved for adults 18+. Shaded double daybeds, poolside champagne sommelier, and tranquil lounge music.",
                "insider_tips": "Reserve Cabana 3 for unmatched panoramic sunset views over the cliffs."
            },
            {
                "id": "REC-SPA-COUPLES",
                "name": "Oceanfront Couples Harmony Spa Ritual",
                "category": "Wellness & Romance",
                "location_type": "resort",
                "distance_km": 0.0,
                "travel_time_minutes": 0,
                "operating_hours": "8:00 AM - 8:00 PM Daily",
                "family_friendly": False,
                "min_age": 18,
                "price_level": "$$$$",
                "tags": ["adults_only", "romance", "couples", "spa", "massage", "on_site"],
                "description": "Side-by-side 90-minute aromatherapy Swedish massage in an oceanfront private suite, followed by 30 minutes in a private hydrotherapy hot tub with chilled Dom Pérignon.",
                "insider_tips": "Ideal for anniversaries or honeymoon celebrations; 8-hour advance reservation required."
            }
        ]

        self.candidates = [RecommendationCandidate(**item) for item in catalog_raw]

        if self.collection.count() == 0:
            ids = [c.id for c in self.candidates]
            docs = [f"{c.name} ({c.category}): {c.description} {c.insider_tips} Tags: {', '.join(c.tags)}" for c in self.candidates]
            metas = [{"id": c.id, "name": c.name, "family_friendly": str(c.family_friendly), "distance_km": c.distance_km} for c in self.candidates]
            self.collection.upsert(ids=ids, documents=docs, metadatas=metas)

    def recommend(
        self,
        query: str,
        profile: Optional[GuestProfile] = None,
        top_n: int = 3
    ) -> RecommendationResponse:
        """Executes multi-criteria personalized recommendation with LLM reasoning."""
        # 1. Derive profile constraints from query & user preferences
        guest_profile = self.extractor.extract_profile(query, base_profile=profile)

        # 2. Compute semantic vector similarity
        vector_results = self.collection.query(
            query_texts=[query],
            n_results=len(self.candidates)
        )
        sim_scores: Dict[str, float] = {}
        if vector_results and vector_results["ids"]:
            ids = vector_results["ids"][0]
            dists = vector_results["distances"][0] if vector_results.get("distances") else [0.5] * len(ids)
            for cid, dist in zip(ids, dists):
                sim_scores[cid] = max(0.0, 1.0 - (dist / 2.0))

        # 3. Score each candidate across multi-criteria dimensions
        scored_list: List[ScoredRecommendation] = []
        for cand in self.candidates:
            semantic_score = sim_scores.get(cand.id, 0.5)
            fam_score = self._compute_family_alignment(cand, guest_profile)
            dist_score = self._compute_distance_score(cand, guest_profile)
            hrs_score = self._compute_hours_score(cand, guest_profile)

            # Composite weighted calculation:
            # Semantic (0.35) + Family Alignment (0.30) + Distance (0.20) + Hours (0.15)
            composite = (
                0.35 * semantic_score +
                0.30 * fam_score +
                0.20 * dist_score +
                0.15 * hrs_score
            )

            # Generate reasoning explanation
            reasoning = self._generate_reasoning(cand, guest_profile, fam_score, dist_score, hrs_score)

            scored_list.append(ScoredRecommendation(
                candidate=cand,
                semantic_similarity=round(semantic_score, 3),
                family_alignment_score=round(fam_score, 3),
                distance_score=round(dist_score, 3),
                hours_score=round(hrs_score, 3),
                composite_score=round(composite, 3),
                personalization_reasoning=reasoning
            ))

        # Sort descending by composite score
        scored_list.sort(key=lambda x: x.composite_score, reverse=True)
        top_recommendations = scored_list[:top_n]

        # 4. Generate LLM Personalized Synthesized Advice
        advice = self._synthesize_personalized_advice(query, guest_profile, top_recommendations)

        return RecommendationResponse(
            query=query,
            guest_profile=guest_profile,
            recommendations=top_recommendations,
            concierge_advice=advice
        )

    def _compute_family_alignment(self, candidate: RecommendationCandidate, profile: GuestProfile) -> float:
        if profile.party_type == "family_with_children":
            if not candidate.family_friendly:
                return 0.05  # Severe penalty for adult-only venues
            # Bonus for dedicated children/family spaces
            if any(t in candidate.tags for t in ["kids_club", "family", "children", "pool"]):
                return 1.0
            return 0.85
        elif profile.party_type == "couple_romantic":
            if not candidate.family_friendly:
                return 1.0  # Adult-only places preferred by couples
            if "romance" in candidate.tags or "scenic" in candidate.tags:
                return 0.95
            return 0.70
        return 0.80

    def _compute_distance_score(self, candidate: RecommendationCandidate, profile: GuestProfile) -> float:
        d = candidate.distance_km
        if d == 0.0:
            score = 1.0
        elif d <= 2.0:
            score = 0.95
        elif d <= 5.0:
            score = 0.85
        elif d <= 10.0:
            score = 0.70
        else:
            score = max(0.2, 1.0 - (d / 30.0))

        # Apply boundary penalty if exceeds max_distance_km
        if d > profile.max_distance_km:
            score *= 0.5
        return score

    def _compute_hours_score(self, candidate: RecommendationCandidate, profile: GuestProfile) -> float:
        target_tod = profile.preferred_time_of_day
        if not target_tod:
            return 1.0
        
        hours_lower = candidate.operating_hours.lower()
        if target_tod == "morning" and ("6:00 am" in hours_lower or "8:00 am" in hours_lower or "9:00 am" in hours_lower):
            return 1.0
        if target_tod == "evening" and ("10:00 pm" in hours_lower or "midnight" in hours_lower or "7:00 pm" in hours_lower or "8:00 pm" in hours_lower):
            return 1.0
        if target_tod == "evening" and ("5:00 pm" in hours_lower and not any(w in hours_lower for w in ["night", "midnight"])):
            return 0.5  # Closes early
        return 0.85

    def _generate_reasoning(
        self,
        candidate: RecommendationCandidate,
        profile: GuestProfile,
        fam_score: float,
        dist_score: float,
        hrs_score: float
    ) -> str:
        points = []
        if profile.party_type == "family_with_children":
            if candidate.family_friendly:
                points.append(f"Ideal for children (certified supervised staff & minimum age {candidate.min_age}+)")
            else:
                points.append("Adults-only venue; not recommended for travel with children")
        elif profile.party_type == "couple_romantic":
            points.append("Exquisite romantic ambiance tailored for couples")

        if candidate.distance_km == 0.0:
            points.append("Located right on-site at the resort (zero travel time)")
        else:
            points.append(f"Located just {candidate.distance_km} km away (~{candidate.travel_time_minutes} mins)")

        points.append(f"Open {candidate.operating_hours}")
        return " • ".join(points)

    def _synthesize_personalized_advice(
        self,
        query: str,
        profile: GuestProfile,
        recommendations: List[ScoredRecommendation]
    ) -> str:
        prompt = f"""{get_system_prompt(PersonaStyle.LUXURY_CLEFS_D_OR)}

GUEST PREFERENCES:
- Party Type: {profile.party_type}
- Max Distance: {profile.max_distance_km} km
- Preferred Time: {profile.preferred_time_of_day or 'Flexible'}
- Stated Query: "{query}"

TOP PERSONALIZED RECOMMENDATIONS (RANKED BY REASONING):
{chr(10).join([f"- {r.candidate.name} (Score: {r.composite_score:.2f}, Distance: {r.candidate.distance_km} km, Hours: {r.candidate.operating_hours}): {r.personalization_reasoning}" for r in recommendations])}

TASK:
Craft a warm, personalized recommendation response as Chief Concierge Julian.
Explain WHY these specific activities were chosen for their travel party (e.g. highlighting child-friendly safety, proximity, and hours if traveling with kids).
Keep it elegant, helpful, and concise (under 200 words).
"""
        messages = [ChatMessage(role="user", content=query)]
        raw_advice = self.llm.generate_response(system_prompt=prompt, messages=messages)

        top_cand_word = recommendations[0].candidate.name.split()[0].lower()
        has_top_mention = top_cand_word in raw_advice.lower() and "welcome to the grand azure" not in raw_advice.lower()
        if len(raw_advice) > 120 and has_top_mention and not raw_advice.startswith("I apologize"):
            return raw_advice

        # Offline personalized synthesis
        recs_text = "\n".join([
            f"• **{r.candidate.name}** ({r.candidate.distance_km} km away, open {r.candidate.operating_hours}): {r.candidate.description} *Insider Tip:* {r.candidate.insider_tips}"
            for r in recommendations
        ])

        if profile.party_type == "family_with_children":
            return (
                f"Traveling with children is such a joyous experience, and I have hand-picked activities "
                f"conveniently close to the resort featuring engaging, safe, and family-approved amenities:\n\n"
                f"{recs_text}\n\n"
                f"We would be delighted to reserve gear or provide our house Mercedes shuttle at your convenience."
            )
        else:
            return (
                f"It is my distinct pleasure to present these tailored suggestions curated to your preferences:\n\n"
                f"{recs_text}\n\n"
                f"Please let me know if you would like me to coordinate reservations or chauffeured transfers."
            )
