"""Module 14: Specialized Restaurant & Dining Agent

Answers comprehensive dining queries:
1. Restaurant timings & hours
2. Cuisine types & culinary concepts
3. Menu information & signature dishes
4. Dietary options & allergen accommodations
5. Seating information (cliffside, courtyard, lounge, wine cellar)
6. Room service information (24/7 schedule, late-night menu, ordering)

Advanced capability:
- Preference-based multi-criteria restaurant recommendations
- Table reservation booking with confirmation tracking
"""

import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.module14_dining_agent.models import (
    DiningQueryType,
    DiningVenueDetails,
    DiningPreferences,
    DiningReservation,
    SeatingArea
)
from src.module14_dining_agent.dining_kb import get_all_dining_venues


class RestaurantDiningAgent:
    """Specialized Concierge Agent for Resort and Destination Dining."""

    def __init__(self):
        self.venues: List[DiningVenueDetails] = get_all_dining_venues()
        self.reservations: List[DiningReservation] = []

    def classify_dining_query(self, query: str) -> DiningQueryType:
        """Categorizes the specific dining aspect being queried."""
        ql = query.lower()
        if any(w in ql for w in ["book a table", "reserve a table", "make a reservation", "reservation for", "book table", "reserve table"]):
            return DiningQueryType.RESERVATION
        if any(w in ql for w in ["time", "hours", "opening", "closing", "open until", "when does", "what time", "schedule"]):
            return DiningQueryType.TIMINGS
        if any(w in ql for w in ["seating", "table view", "terrace", "outdoor", "balcony", "cliffside", "cabana", "patio", "where to sit", "view"]):
            return DiningQueryType.SEATING
        if any(w in ql for w in ["dietary", "vegan", "vegetarian", "gluten", "halal", "allergy", "dairy-free", "celiac"]):
            return DiningQueryType.DIETARY
        if any(w in ql for w in ["room service", "in-room dining", "delivered to room", "late night menu", "order to my room"]):
            return DiningQueryType.ROOM_SERVICE
        if any(w in ql for w in ["menu", "dish", "dishes", "food", "signature", "what to eat", "price", "cost"]):
            return DiningQueryType.MENU
        if any(w in ql for w in ["cuisine", "type of food", "style", "french", "seafood", "mediterranean", "italian"]):
            return DiningQueryType.CUISINE
        if any(w in ql for w in ["recommend", "suggest", "where should", "best place", "romantic dinner", "for a couple", "family dinner"]):
            return DiningQueryType.RECOMMENDATION
        return DiningQueryType.GENERAL

    def answer_dining_query(self, query: str, preferences: Optional[DiningPreferences] = None) -> Dict[str, Any]:
        """Provides expert dining answers grounded in resort venues and menus."""
        q_type = self.classify_dining_query(query)
        ql = query.lower()

        # Target specific venue if mentioned
        target_venue: Optional[DiningVenueDetails] = None
        for v in self.venues:
            if v.name.lower() in ql or any(w in ql for w in v.name.lower().split() if len(w) > 4):
                target_venue = v
                break

        # 1. TIMINGS
        if q_type == DiningQueryType.TIMINGS:
            return self._handle_timings(target_venue)

        # 2. CUISINE
        if q_type == DiningQueryType.CUISINE:
            return self._handle_cuisine(target_venue)

        # 3. MENU INFORMATION
        if q_type == DiningQueryType.MENU:
            return self._handle_menu(target_venue)

        # 4. DIETARY OPTIONS
        if q_type == DiningQueryType.DIETARY:
            return self._handle_dietary(ql, target_venue)

        # 5. SEATING INFORMATION
        if q_type == DiningQueryType.SEATING:
            return self._handle_seating(target_venue)

        # 6. ROOM SERVICE INFORMATION
        if q_type == DiningQueryType.ROOM_SERVICE:
            return self._handle_room_service()

        # 7. RECOMMENDATION
        if q_type == DiningQueryType.RECOMMENDATION:
            prefs = preferences or self._extract_preferences_from_text(query)
            return self.recommend_dining(prefs)

        # 8. RESERVATION
        if q_type == DiningQueryType.RESERVATION:
            return self._handle_reservation_intent(query)

        # General Dining Overview
        return self._handle_general_overview()

    def recommend_dining(self, prefs: DiningPreferences) -> Dict[str, Any]:
        """Advanced recommendation engine matching atmosphere, cuisine, dietary, and party."""
        scored_venues = []

        for v in self.venues:
            score = 1.0
            reasons = []

            # Match meal period
            if prefs.meal_period == "breakfast" and "Azure" not in v.name and "Room" not in v.name:
                score -= 0.5
            elif prefs.meal_period == "late_night" and not v.room_service_available and "Sunset" not in v.name:
                score -= 0.6

            # Match atmosphere
            if prefs.atmosphere_preference == "romantic":
                if "Azure" in v.name or "Jardin" in v.name:
                    score += 0.4
                    reasons.append("Spectacular romantic ocean/garden ambiance")
            elif prefs.atmosphere_preference == "casual":
                if "Sunset" in v.name or "Room" in v.name:
                    score += 0.3
                    reasons.append("Relaxed resort casual atmosphere")

            # Match dietary restrictions
            if prefs.dietary_restrictions:
                matched_diets = [d for d in prefs.dietary_restrictions if any(d.lower() in opt.lower() for opt in v.dietary_options)]
                if matched_diets:
                    score += 0.3
                    reasons.append(f"Dedicated {', '.join(matched_diets)} culinary selections")

            # Match cuisine
            if prefs.cuisine and prefs.cuisine.lower() in v.cuisine_type.lower():
                score += 0.5
                reasons.append(f"Direct match for {prefs.cuisine} cuisine")

            # Match seating preference
            if prefs.preferred_seating:
                for s in v.seating_areas:
                    if prefs.preferred_seating.lower() in s.name.lower() or prefs.preferred_seating.lower() in s.view.lower():
                        score += 0.3
                        reasons.append(f"Features {s.name} ({s.view})")
                        break

            scored_venues.append((score, v, reasons))

        scored_venues.sort(key=lambda x: x[0], reverse=True)
        top_venue = scored_venues[0][1]
        top_reasons = scored_venues[0][2]

        reply_lines = [
            f"Based on your dining preferences for a party of {prefs.party_size} ({prefs.atmosphere_preference} atmosphere), "
            f"I warmly recommend **{top_venue.name}**:\n",
            f"• **Cuisine:** {top_venue.cuisine_type} ({top_venue.price_level})",
            f"• **Location:** {top_venue.location}",
            f"• **Why It Suits You:** {'; '.join(top_reasons) if top_reasons else 'Exquisite culinary quality and service'}.",
            f"• **Signature Dish:** {top_venue.signature_dishes[0] if top_venue.signature_dishes else 'Chef Daily Feature'}",
            f"• **Seating Recommendation:** {top_venue.seating_areas[0].name} ({top_venue.seating_areas[0].atmosphere})\n",
            f"Would you like me to reserve a premier table for your party this evening?"
        ]

        return {
            "query_type": DiningQueryType.RECOMMENDATION.value,
            "recommended_venue": top_venue.name,
            "match_score": scored_venues[0][0],
            "reasons": top_reasons,
            "reply": "\n".join(reply_lines)
        }

    def book_table(
        self,
        venue_name: str,
        guest_name: str = "Esteemed Guest",
        room_number: str = "302",
        party_size: int = 2,
        reservation_date: str = "Tomorrow",
        time_slot: str = "7:30 PM",
        seating_preference: Optional[str] = "Cliffside Sunset Terrace",
        special_requests: str = "Anniversary celebration table"
    ) -> DiningReservation:
        """Creates and stores a confirmed dining reservation."""
        conf_code = f"RES-{venue_name[:5].upper().replace(' ', '')}-{uuid.uuid4().hex[:4].upper()}"
        res = DiningReservation(
            reservation_id=str(uuid.uuid4()),
            confirmation_code=conf_code,
            venue_name=venue_name,
            guest_name=guest_name,
            room_number=room_number,
            party_size=party_size,
            reservation_date=reservation_date,
            time_slot=time_slot,
            seating_area=seating_preference or "Main Dining Room",
            special_requests=special_requests,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.reservations.append(res)
        return res

    # ------------------------------------------------------------------------
    # Private Category Handlers
    # ------------------------------------------------------------------------

    def _handle_timings(self, target: Optional[DiningVenueDetails]) -> Dict[str, Any]:
        if target:
            hours_str = "\n".join(f"  • **{k}:** {v}" for k, v in target.hours.items())
            reply = (
                f"Operating hours for **{target.name}**:\n{hours_str}\n\n"
                f"• **Dress Code:** {target.dress_code}\n"
                f"• **Reservations:** {'Recommended / Required' if target.reservation_required else 'Walk-ins welcome'}"
            )
            return {"query_type": "timings", "venue": target.name, "hours": target.hours, "reply": reply}

        lines = ["Here are the dining hours across The Grand Azure Resort & Spa:\n"]
        for v in self.venues:
            h = list(v.hours.values())[0] if v.hours else "Open daily"
            lines.append(f"• **{v.name}**: {h}")
        lines.append("\nOur In-Room Dining team is at your command 24 hours a day.")
        return {"query_type": "timings", "reply": "\n".join(lines)}

    def _handle_cuisine(self, target: Optional[DiningVenueDetails]) -> Dict[str, Any]:
        if target:
            reply = (
                f"**{target.name}** features exceptional **{target.cuisine_type}**.\n\n"
                f"• **Dining Style:** {target.dining_style} ({target.price_level})\n"
                f"• **Location:** {target.location}\n"
                f"• **Culinary Note:** {target.chef_notes or 'Prepared with seasonal coastal ingredients.'}"
            )
            return {"query_type": "cuisine", "venue": target.name, "cuisine": target.cuisine_type, "reply": reply}

        lines = ["Our resort celebrates distinguished culinary diversity:\n"]
        for v in self.venues:
            lines.append(f"• **{v.name}**: {v.cuisine_type} ({v.dining_style})")
        return {"query_type": "cuisine", "reply": "\n".join(lines)}

    def _handle_menu(self, target: Optional[DiningVenueDetails]) -> Dict[str, Any]:
        v = target or self.venues[0]
        dishes = "\n".join(f"  • {d}" for d in v.signature_dishes)
        reply = (
            f"Signature culinary highlights at **{v.name}**:\n{dishes}\n\n"
            f"• **Price Tier:** {v.price_level}\n"
            f"• **Dietary Selections:** {', '.join(v.dietary_options)}\n\n"
            "Would you like me to share wine pairings or arrange a reservation?"
        )
        return {"query_type": "menu", "venue": v.name, "dishes": v.signature_dishes, "reply": reply}

    def _handle_dietary(self, ql: str, target: Optional[DiningVenueDetails]) -> Dict[str, Any]:
        lines = ["We cater with meticulous attention to all dietary requirements and allergies:\n"]
        for v in self.venues:
            lines.append(f"• **{v.name}**: Offers {', '.join(v.dietary_options)}")
        lines.append(
            "\nOur culinary brigade can prepare fully customized allergen-free, vegan, kosher-style, "
            "or halal-certified meals with 2 hours advance notice. Kindly inform us of any severe allergies."
        )
        return {"query_type": "dietary", "reply": "\n".join(lines)}

    def _handle_seating(self, target: Optional[DiningVenueDetails]) -> Dict[str, Any]:
        v = target or self.venues[0]
        lines = [f"Distinctive seating atmospheres at **{v.name}**:\n"]
        for s in v.seating_areas:
            lines.append(f"• **{s.name}** ({s.location_desc}): {s.atmosphere}. *View:* {s.view}")
        lines.append("\nI would be delighted to reserve your preferred seating section in advance.")
        return {"query_type": "seating", "venue": v.name, "seating": [s.model_dump() for s in v.seating_areas], "reply": "\n".join(lines)}

    def _handle_room_service(self) -> Dict[str, Any]:
        reply = (
            "🛎️ **The Grand Azure In-Room Dining (24/7 Room Service)**\n\n"
            "• **Availability:** 24 Hours Daily around the clock\n"
            "• **Late-Night Menu:** Available 11:00 PM to 6:00 AM (featuring artisan Wagyu burgers, wood-fired pizzas, organic acai bowls, and soups)\n"
            "• **Delivery Turnaround:** 20 to 30 minutes to all rooms and private villas\n"
            "• **Special Presentation:** Balcony linen service or breakfast in bed setup upon request\n"
            "• **To Order:** Dial Extension 4 or inform me directly with your selections."
        )
        return {"query_type": "room_service", "reply": reply}

    def _handle_reservation_intent(self, query: str) -> Dict[str, Any]:
        # Extract party size and time if mentioned
        party = 2
        p_match = re.search(r'\b(?:for|party of)\s*([0-9]+)\b', query.lower())
        if p_match:
            party = int(p_match.group(1))

        time_val = "7:30 PM"
        t_match = re.search(r'\b([0-9]{1,2}(?::[0-9]{2})?\s*(?:am|pm)?)\b', query.lower())
        if t_match and any(w in t_match.group(1).lower() for w in ["am", "pm", ":"]):
            time_val = t_match.group(1).upper()

        venue = self.venues[0].name
        for v in self.venues:
            if v.name.lower() in query.lower():
                venue = v.name
                break

        res = self.book_table(
            venue_name=venue,
            guest_name="Esteemed Guest",
            party_size=party,
            time_slot=time_val
        )

        reply = (
            f"It is my absolute pleasure to confirm your table reservation!\n\n"
            f"• **Venue:** {res.venue_name}\n"
            f"• **Confirmation Code:** `{res.confirmation_code}`\n"
            f"• **Party Size:** {res.party_size} guests\n"
            f"• **Date & Time:** {res.reservation_date} at {res.time_slot}\n"
            f"• **Seating Area:** {res.seating_area}\n\n"
            "The maître d' has been personally notified. May I arrange chauffeur transport or flowers for your table?"
        )
        return {"query_type": "reservation", "reservation": res.model_dump(), "reply": reply}

    def _handle_general_overview(self) -> Dict[str, Any]:
        lines = [
            "Welcome to The Grand Azure Resort dining collection. We offer four culinary destinations:\n",
            "1. **Azure Breeze Seafood Grill** — Fine Mediterranean catches & sunset terrace",
            "2. **Le Jardin French Bistro** — Modern Provençal cuisine in our botanical courtyard",
            "3. **Sunset Cliffside Lounge & Raw Bar** — Artisanal tapas, sushi, and craft mixology",
            "4. **In-Room Dining** — 24/7 gourmet delivery to your suite or private villa\n",
            "How may I curate your culinary experience today?"
        ]
        return {"query_type": "general", "reply": "\n".join(lines)}

    def _extract_preferences_from_text(self, text: str) -> DiningPreferences:
        tl = text.lower()
        vibe = "scenic"
        if "romantic" in tl or "couple" in tl or "anniversary" in tl:
            vibe = "romantic"
        elif "casual" in tl or "quick" in tl:
            vibe = "casual"
        elif "family" in tl or "kids" in tl or "children" in tl:
            vibe = "family"

        diets = []
        for d in ["vegan", "vegetarian", "gluten-free", "halal"]:
            if d in tl:
                diets.append(d.title())

        party = 2
        p_match = re.search(r'\b([1-9]|10)\s*(?:people|guests|persons)?\b', tl)
        if p_match:
            party = int(p_match.group(1))

        return DiningPreferences(
            party_size=party,
            atmosphere_preference=vibe,
            dietary_restrictions=diets
        )
