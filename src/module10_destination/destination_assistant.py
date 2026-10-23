"""Module 10: Local Destination Assistant

Concierge specialist for the wider region beyond the hotel:
- Attractions & Cultural Sights
- Regional Dining
- Shopping & Artisan Quarters
- Transportation Logistics
- Tourist Viewpoints
- Curated Half-Day & Full-Day Itineraries
"""

from typing import List, Dict, Any, Optional
from src.module10_destination.models import (
    DestinationCategory,
    DestinationItem,
    DestinationSearchResponse,
    CuratedItinerary,
    ItineraryStop
)
from src.module10_destination.destination_search import DestinationSemanticSearch
from src.module4_concierge.persona import PersonaStyle, get_system_prompt
from src.module4_concierge.llm_backend import LLMBackend
from src.module4_concierge.memory import ChatMessage


class LocalDestinationAssistant:
    """Intelligent Concierge specializing in regional destination discovery & logistics."""

    def __init__(
        self,
        search_engine: Optional[DestinationSemanticSearch] = None,
        provider: str = "auto"
    ):
        self.search = search_engine or DestinationSemanticSearch()
        self.llm = LLMBackend(provider=provider)

    def answer_destination_query(
        self,
        query: str,
        category: Optional[DestinationCategory] = None,
        max_distance_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """Provides a grounded concierge response with semantic search results and transit options."""
        # 1. Semantic search across destination items
        search_resp = self.search.search(
            query=query,
            category=category,
            max_distance_km=max_distance_km,
            top_k=3
        )

        # 2. Prepare grounded context block
        context_lines = []
        for r in search_resp.results:
            item = r.item
            context_lines.append(
                f"• {item.name} ({item.category.value.title()} - {item.sub_category}):\n"
                f"  Distance: {item.distance_km} km ({item.travel_time_minutes} mins via {', '.join(item.transit_options[:2])})\n"
                f"  Hours: {item.operating_hours} | Price: {item.price_level}\n"
                f"  Highlights: {', '.join(item.highlights)}\n"
                f"  Insider Tip: {item.concierge_tips}\n"
            )
        context_block = "\n".join(context_lines)

        system_prompt = f"""{get_system_prompt(PersonaStyle.LUXURY_CLEFS_D_OR)}

VERIFIED REGIONAL DESTINATION KNOWLEDGE:
================================================================================
{context_block}
================================================================================

TASK:
Answer the guest's destination question with warm sophistication.
Include exact distances, travel times, transit recommendations, and insider tips from the verified knowledge above.
Maintain the persona of Chief Concierge Julian.
"""

        messages = [ChatMessage(role="user", content=query)]
        raw_reply = self.llm.generate_response(system_prompt=system_prompt, messages=messages)

        # Enhance reply if local generator produced generic greeting
        top_name = search_resp.results[0].item.name.split()[0].lower() if search_resp.results else ""
        if len(raw_reply) < 100 or top_name not in raw_reply.lower() or "welcome to the grand azure" in raw_reply.lower():
            reply_parts = [
                f"It is my distinct pleasure to guide your regional exploration, esteemed guest. Based on your interest in *\"{query}\"*, here are my premier recommendations:\n"
            ]
            for r in search_resp.results:
                it = r.item
                reply_parts.append(
                    f"• **{it.name}** ({it.distance_km} km away, ~{it.travel_time_minutes} mins)\n"
                    f"  *Transit:* {', '.join(it.transit_options)}\n"
                    f"  *Highlights:* {', '.join(it.highlights[:3])}\n"
                    f"  *Julian's Tip:* {it.concierge_tips}\n"
                )
            reply_parts.append(
                "Our house electric shuttle departs from the main entrance every 30 minutes, or I would be delighted to arrange a private Mercedes chauffeur for your party."
            )
            raw_reply = "\n".join(reply_parts)

        return {
            "query": query,
            "answer": raw_reply,
            "total_matches": search_resp.total_found,
            "search_results": search_resp.results,
            "top_match": search_resp.results[0].item if search_resp.results else None
        }

    def create_curated_itinerary(self, theme: str = "cultural_and_coastal") -> CuratedItinerary:
        """Constructs an exquisite full-day or half-day curated local itinerary."""
        stops = [
            ItineraryStop(
                time_slot="9:30 AM - 11:30 AM",
                item=self.search.items["DEST-ATT-001"],
                activity_description="Explore the bioluminescent sea grottos and crystalline caverns via guided kayak before the midday sun.",
                transit_guidance="Resort private eco-boat departs directly from the Azure Beach Club dock at 9:15 AM."
            ),
            ItineraryStop(
                time_slot="12:30 PM - 2:00 PM",
                item=self.search.items["DEST-REST-001"],
                activity_description="Leisurely waterfront lunch featuring handmade pasta and salt-crusted sea bass at harbor-side Table 12.",
                transit_guidance="5-minute scenic cruise on the resort shuttle boat to Marina Promenade."
            ),
            ItineraryStop(
                time_slot="2:30 PM - 4:30 PM",
                item=self.search.items["DEST-SHOP-001"],
                activity_description="Stroll the cobblestone artisan quarter for custom perfume blending and ceramic atelier visits.",
                transit_guidance="Complimentary electric shuttle from Marina to Old Town Citadel Gate."
            ),
            ItineraryStop(
                time_slot="5:30 PM - 7:30 PM",
                item=self.search.items["DEST-TOUR-001"],
                activity_description="Climb the 17th-century bastion ramparts for panoramic sunset views and the evening cannon ceremony.",
                transit_guidance="10-minute walk from the artisan market to the citadel summit; return via resort Mercedes."
            )
        ]

        return CuratedItinerary(
            title="The Grand Azure Grand Regional Odyssey",
            theme="Coastal Nature, Gastronomy, Artisan Shopping & Citadel History",
            recommended_for="Couples, Families with older children, and Discerning Travelers",
            stops=stops,
            total_duration_hours=10.0,
            concierge_notes="All VIP reservations, tickets, and round-trip transfers are seamlessly coordinated by the Concierge desk."
        )
