"""Module 9: Guest Preference Extractor

Extracts explicit and implicit personalization dimensions:
- Travel party (family with children, couples, solo, business)
- Distance preferences (nearby <3km, walkable, day trip)
- Schedule & opening hours awareness
- Interests & special occasions
"""

import re
from typing import Optional
from src.module9_recommendations.models import GuestProfile


class PreferenceExtractor:
    """Extracts a structured GuestProfile from natural language inquiries."""

    def extract_profile(self, query: str, base_profile: Optional[GuestProfile] = None) -> GuestProfile:
        profile = base_profile.model_copy() if base_profile else GuestProfile()
        lower = query.lower()

        # 1. Family with children
        if any(w in lower for w in [
            "with children", "with kids", "with toddlers", "family", "traveling with my kids",
            "traveling with children", "my daughter", "my son", "family-friendly"
        ]):
            profile.party_type = "family_with_children"
            profile.children_count = max(1, profile.children_count)
            if "family_activities" not in profile.interests:
                profile.interests.append("family_activities")

        # 2. Romantic / Couple
        elif any(w in lower for w in ["anniversary", "honeymoon", "romantic", "my wife and i", "my husband and i", "couple"]):
            profile.party_type = "couple_romantic"
            if "anniversary" in lower:
                profile.special_occasion = "Anniversary"
            if "romantic_dining" not in profile.interests:
                profile.interests.append("romantic_dining")

        # 3. Solo / Wellness
        elif any(w in lower for w in ["solo", "by myself", "relaxation", "quiet time", "peaceful retreat"]):
            profile.party_type = "solo_wellness"
            if "wellness" not in profile.interests:
                profile.interests.append("wellness")

        # 4. Distance / Proximity Preferences
        if any(w in lower for w in ["nearby", "close by", "walking distance", "short walk", "around the corner"]):
            profile.max_distance_km = 3.5
        elif any(w in lower for w in ["day trip", "excursion", "driving distance", "explore the region"]):
            profile.max_distance_km = 25.0

        # 5. Time of Day
        if any(w in lower for w in ["morning", "breakfast time", "early"]):
            profile.preferred_time_of_day = "morning"
        elif any(w in lower for w in ["afternoon", "lunch time", "midday"]):
            profile.preferred_time_of_day = "afternoon"
        elif any(w in lower for w in ["evening", "tonight", "dinner", "sunset", "night"]):
            profile.preferred_time_of_day = "evening"

        # 6. Specific Interests
        interest_keywords = {
            "nature": ["nature", "scenic", "gardens", "outdoors", "caves", "view"],
            "water_sports": ["kayak", "paddleboard", "swim", "pool", "beach", "boat", "yacht"],
            "culture": ["museum", "history", "citadel", "historic", "artisan", "perfume"],
            "shopping": ["shop", "boutiques", "shopping", "promenade", "market"],
            "wellness": ["spa", "massage", "facial", "yoga", "sauna"]
        }
        for interest, kws in interest_keywords.items():
            if any(kw in lower for kw in kws) and interest not in profile.interests:
                profile.interests.append(interest)

        return profile
