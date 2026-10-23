"""Module 7: Hotel Service Knowledge Assistant

Provides intelligent, grounded answers and request handling for 9 core hotel services:
Housekeeping, Laundry, Room Service, Wi-Fi, Parking, Gym, Pool, Spa, and Restaurants.
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime

from src.module7_service_kb.models import (
    ServiceCategory,
    ServiceQuery,
    ServiceResponse,
    ServiceRequest
)
from src.module7_service_kb.service_collections import ServiceCollectionManager
from src.module4_concierge.persona import PersonaStyle, get_system_prompt
from src.module4_concierge.llm_backend import LLMBackend
from src.module4_concierge.memory import ChatMessage


class HotelServiceAssistant:
    """Intelligent Assistant for Hotel Services Knowledge & Requests."""

    def __init__(
        self,
        collection_manager: Optional[ServiceCollectionManager] = None,
        provider: str = "auto"
    ):
        self.manager = collection_manager or ServiceCollectionManager()
        self.llm = LLMBackend(provider=provider)
        self.logged_requests: List[ServiceRequest] = []

    def answer_service_query(
        self,
        query: str,
        category: Optional[ServiceCategory] = None,
        guest_context: Optional[Dict[str, Any]] = None
    ) -> ServiceResponse:
        """Answers a hotel service inquiry with grounded knowledge and actionable options."""
        guest_context = guest_context or {}
        
        # 1. Determine or verify service category
        resolved_category = category or self.manager.route_query_to_service(query)

        # 2. Retrieve grounded knowledge from the dedicated service collection
        chunks = self.manager.retrieve_from_service(resolved_category, query, top_k=3)
        context_text = "\n\n".join([f"[{c['metadata'].get('title', 'Service Info')}]\n{c['content']}" for c in chunks])

        # 3. Check if query is an actionable request (e.g., asking to deliver, book, clean, order)
        is_actionable, action_type = self._detect_actionable_intent(query, resolved_category)

        # 4. Generate structured response
        grounded_prompt = f"""{get_system_prompt(PersonaStyle.LUXURY_CLEFS_D_OR)}

VERIFIED SERVICE KNOWLEDGE ({resolved_category.value.upper()}):
================================================================================
{context_text}
================================================================================

INSTRUCTIONS:
1. Provide a warm, refined, and accurate answer grounded strictly in the verified knowledge above.
2. Clearly state relevant hours, prices, turnaround times, or requirements.
3. If the guest is requesting an actionable item or delivery, acknowledge it and explain next steps.
4. Keep the response elegant and helpful.
"""

        messages = [
            ChatMessage(role="user", content=f"Guest inquiry regarding {resolved_category.value}: '{query}'")
        ]

        raw_answer = self.llm.generate_response(system_prompt=grounded_prompt, messages=messages)

        # Enhance response with specific facts if running offline
        refined_answer = self._synthesize_service_answer(
            query=query,
            category=resolved_category,
            raw_answer=raw_answer,
            chunks=chunks,
            is_actionable=is_actionable
        )

        # 5. Extract suggested actions and contact extension
        suggested_actions = self._generate_suggested_actions(resolved_category, is_actionable)
        contact_info = self._get_service_contact(resolved_category)

        # 6. Log request if actionable and room number is provided
        room_number = guest_context.get("room_number") or self._extract_room_number(query)
        if is_actionable:
            req = ServiceRequest(
                category=resolved_category,
                description=query,
                room_number=room_number,
                guest_name=guest_context.get("guest_name"),
                priority="high" if any(w in query.lower() for w in ["urgent", "immediately", "asap", "hurry"]) else "normal",
                status="dispatched" if room_number else "pending_room_confirmation"
            )
            self.logged_requests.append(req)

        return ServiceResponse(
            category=resolved_category,
            answer=refined_answer,
            details={
                "retrieved_chunks_count": len(chunks),
                "top_source": chunks[0]["metadata"].get("title") if chunks else None,
                "is_actionable": is_actionable,
                "room_number": room_number
            },
            actionable=is_actionable,
            suggested_actions=suggested_actions,
            contact=contact_info
        )

    def _detect_actionable_intent(self, query: str, category: ServiceCategory) -> Tuple[bool, Optional[str]]:
        """Detects whether the guest is seeking information or requesting an immediate action."""
        q = query.lower()
        action_triggers = ["send", "bring", "deliver", "order", "book", "reserve", "pickup", "clean", "need", "can i get", "please provide"]
        
        for trigger in action_triggers:
            if trigger in q:
                return True, trigger
        return False, None

    def _extract_room_number(self, query: str) -> Optional[str]:
        match = re.search(r'\b(?:room|suite|villa)\s+([0-9a-zA-Z]+)\b', query.lower())
        return match.group(1).upper() if match else None

    def _generate_suggested_actions(self, category: ServiceCategory, is_actionable: bool) -> List[str]:
        suggestions_map = {
            ServiceCategory.HOUSEKEEPING: ["Request Fresh Towels", "Select Pillows from Menu", "Request Evening Turndown", "Request Baby Crib"],
            ServiceCategory.LAUNDRY: ["Request 4-Hour Express Pickup", "Schedule Standard 24h Laundry", "Request Garment Pressing"],
            ServiceCategory.ROOM_SERVICE: ["Order Wagyu Burger & Fries", "Request Coastal Benedict Breakfast", "View All-Day In-Room Menu"],
            ServiceCategory.WIFI: ["Connect to GrandAzure_Guest", "Upgrade to 300 Mbps Ultra Premium", "Contact IT Concierge (Ext. 777)"],
            ServiceCategory.PARKING: ["Request Valet Car Retrieval", "Locate Tesla EV Superchargers", "Review Self-Parking Garage Access"],
            ServiceCategory.GYM: ["Book 1-on-1 Personal Trainer", "Reserve Morning Sunrise Yoga", "Check Fitness Pavilion Equipment"],
            ServiceCategory.POOL: ["Reserve Cliffside VIP Cabana", "View Serenity Adults Pool Hours", "Request Pool Towel Service"],
            ServiceCategory.SPA: ["Book Ocean Harmony Couples Massage", "Reserve Caviar Radiance Facial", "Schedule Thalassotherapy Thermal Circuit"],
            ServiceCategory.RESTAURANTS: ["Reserve Table at Azure Breeze", "Book French Bistro Sunday Brunch", "View Sunset Lounge Cocktail Menu"]
        }
        return suggestions_map.get(category, ["Contact Concierge Desk"])

    def _get_service_contact(self, category: ServiceCategory) -> str:
        contact_map = {
            ServiceCategory.HOUSEKEEPING: "Dial 2 for Housekeeping Dispatch",
            ServiceCategory.LAUNDRY: "Dial 4 for Valet Laundry & Garment Care",
            ServiceCategory.ROOM_SERVICE: "Dial 5 for 24/7 In-Room Dining",
            ServiceCategory.WIFI: "Dial 777 for On-Site IT Concierge Support",
            ServiceCategory.PARKING: "Dial 0 or text 'RETRIEVE [Ticket#]' to Valet",
            ServiceCategory.GYM: "Dial 720 for Fitness Pavilion Desk",
            ServiceCategory.POOL: "Dial 730 for Poolside Concierge & Cabanas",
            ServiceCategory.SPA: "Dial 710 for The Azure Wellness Spa",
            ServiceCategory.RESTAURANTS: "Dial 3 for Restaurant Reservations"
        }
        return contact_map.get(category, "Dial 0 for Front Desk & Concierge")

    def _synthesize_service_answer(
        self,
        query: str,
        category: ServiceCategory,
        raw_answer: str,
        chunks: List[Dict[str, Any]],
        is_actionable: bool
    ) -> str:
        """Enriches the answer with exact grounded figures and polite phrasing."""
        # Check if LLM response already contains factual grounded details
        has_specific_facts = any(c in raw_answer for c in ["$", ":", "%", "hours", "AM", "PM", "24/7"])
        if len(raw_answer) > 100 and has_specific_facts and not raw_answer.startswith("I apologize"):
            return raw_answer

        # Offline / Grounded synthesis using verified knowledge
        intro = f"It is my pleasure to assist you with our {category.value.replace('_', ' ').title()} services at The Grand Azure Resort."
        
        facts = []
        if category == ServiceCategory.HOUSEKEEPING:
            facts.append("Daily morning housekeeping is provided between 8:30 AM and 2:30 PM, with evening turndown service from 6:00 PM to 9:00 PM featuring artisan lavender chocolates.")
            facts.append("Plush bath towels, feather or memory foam pillows, Dyson hair dryers, and complimentary baby cribs can be delivered to your room within 15-20 minutes.")
        elif category == ServiceCategory.LAUNDRY:
            facts.append("We provide standard valet laundry with a 24-hour turnaround, as well as an express 4-hour service (50% surcharge).")
            facts.append("Eco dry cleaning is $35 for 2-piece suits, $18 for trousers, and $16 for silk blouses. Suite and Villa guests enjoy 2 complimentary pressed garments per day.")
        elif category == ServiceCategory.ROOM_SERVICE:
            facts.append("In-Room Dining is available 24 hours daily. Breakfast is served from 6:00 AM to 11:00 AM, All-Day Dining until 11:00 PM, and a dedicated late-night menu overnight.")
            facts.append("Delivery takes approximately 30-45 minutes and includes options such as our signature Grand Azure Wagyu Burger, artisan pizzas, and organic acai bowls.")
        elif category == ServiceCategory.WIFI:
            facts.append("Complimentary high-speed internet ('GrandAzure_Guest') offers 50 Mbps across all rooms, pools, and gardens for up to 5 devices per room.")
            facts.append("For bandwidth-heavy needs, 'GrandAzure_Ultra_Premium' provides 300 Mbps low-latency connectivity (complimentary for Suites and Villas, or $15/day).")
        elif category == ServiceCategory.PARKING:
            facts.append("Overnight valet parking is $45 per night with unlimited in/out privileges and an 8-minute retrieval time via SMS.")
            facts.append("Self-parking is available in our covered garage for $25 per night. We also feature complimentary Level 2 and Tesla Superchargers for registered guests.")
        elif category == ServiceCategory.GYM:
            facts.append("The Oceanfront Fitness Pavilion is open 24/7 with your room keycard, equipped with Technogym Artis cardio, Peloton bikes, and free weights up to 100 lbs.")
            facts.append("Complimentary oceanfront sunrise yoga takes place daily at 7:30 AM, and certified personal trainers are available ($120/hour).")
        elif category == ServiceCategory.POOL:
            facts.append("Our heated Cliffside Infinity Pool (82°F) is open 6:00 AM to 10:00 PM. We also offer the adults-only Serenity Pool (84°F, 8:00 AM - 8:00 PM) and a zero-entry Family Splash Lagoon.")
            facts.append("Luxury private cabana rentals are available for $150 half-day or $250 full-day, including dedicated attendant and fresh fruit platters.")
        elif category == ServiceCategory.SPA:
            facts.append("The Azure Wellness Spa operates daily from 8:00 AM to 8:00 PM. Signature treatments include the 80-minute Azure Deep Mineral Recovery Massage ($280) and Cellular Radiance Caviar Facial ($240).")
            facts.append("Guests booking any 60-minute treatment enjoy complimentary access to our seawater Thalassotherapy & Thermal Vitality Circuit.")
        elif category == ServiceCategory.RESTAURANTS:
            facts.append("Our dining collection includes Azure Breeze Seafood Grill (5:30 PM - 10:30 PM dinner, smart casual), Le Jardin French Bistro, and Sunset Cliffside Lounge & Raw Bar.")
            facts.append("Reservations are recommended for dinner; please dial extension 3 to secure prime terrace seating.")

        answer_parts = [intro, " ".join(facts)]
        if is_actionable:
            answer_parts.append("I have logged this request and our concierge dispatch team will attend to it promptly.")
        
        return "\n\n".join(answer_parts)
