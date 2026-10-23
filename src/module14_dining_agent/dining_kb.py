"""Module 14: Dining Knowledge Base & Seating Repository

Enriches resort and local dining records with seating layouts, dietary indexes,
and room service schedules.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any

from src.config import DATA_DIR
from src.module14_dining_agent.models import DiningVenueDetails, SeatingArea


def get_all_dining_venues() -> List[DiningVenueDetails]:
    """Loads all resort dining venues enriched with seating sections and chef notes."""
    raw_venues = []
    dining_file = DATA_DIR / "dining.json"
    if dining_file.exists():
        with open(dining_file, "r", encoding="utf-8") as f:
            raw_venues = json.load(f)

    # Detailed seating configurations per venue
    seating_map = {
        "DIN-AZURE": [
            SeatingArea(
                area_id="AZ-CLIFF",
                name="Cliffside Sunset Terrace",
                location_desc="Outdoor panoramic deck overlooking Azure Bay",
                atmosphere="Romantic, breezy, spectacular golden hour views",
                view="180-degree unobstructed ocean sunset",
                requires_advance_booking=True
            ),
            SeatingArea(
                area_id="AZ-SALON",
                name="Main Marine Dining Salon",
                location_desc="Indoor climate-controlled dining hall",
                atmosphere="Elegant, classical live acoustic guitar",
                view="Floor-to-ceiling glass ocean panorama",
                requires_advance_booking=False
            ),
            SeatingArea(
                area_id="AZ-CELLAR",
                name="Sommelier's Private Wine Cave",
                location_desc="Subterranean limestone wine cellar",
                atmosphere="Intimate, candlelit, tasting menu exclusive",
                view="Surrounded by 3,500 vintage bottles",
                requires_advance_booking=True
            )
        ],
        "DIN-JARDIN": [
            SeatingArea(
                area_id="JAR-COURT",
                name="Botanical Garden Courtyard",
                location_desc="Open-air patio encircled by jasmine and lemon trees",
                atmosphere="Provencal charm, gently bubbling marble fountain",
                view="Botanical garden sculpture walk",
                requires_advance_booking=True
            ),
            SeatingArea(
                area_id="JAR-CONSERV",
                name="The Glass Greenhouse Conservatory",
                location_desc="Enclosed wrought-iron Victorian greenhouse",
                atmosphere="Lush tropical greenery, warm and airy",
                view="Interior garden displays and star canopy",
                requires_advance_booking=False
            )
        ],
        "DIN-SUNSET": [
            SeatingArea(
                area_id="SUN-FIRE",
                name="Infinity Firepit Lounge",
                location_desc="Sunken lounge sofas beside illuminated linear firepits",
                atmosphere="Vibrant, chic chillout lounge with resident DJ",
                view="Infinity edge pool merging into horizon",
                requires_advance_booking=False
            ),
            SeatingArea(
                area_id="SUN-CABANA",
                name="Overwater VIP Sunset Cabanas",
                location_desc="Private teak cabanas suspended over reflection pool",
                atmosphere="Ultra-private luxury bottle service",
                view="Direct sunset view across the bay",
                requires_advance_booking=True
            )
        ],
        "DIN-ROOMSVC": [
            SeatingArea(
                area_id="RMS-BALCONY",
                name="Private Guest Balcony Setup",
                location_desc="Set up with linen tablecloths on guest room terrace",
                atmosphere="Private and intimate dining in guest quarters",
                view="Room specific view (Ocean, Garden, or Bay)",
                requires_advance_booking=False
            )
        ]
    }

    venues = []
    for r in raw_venues:
        vid = r.get("id", "")
        seating = seating_map.get(vid, [
            SeatingArea(
                area_id=f"{vid}-STD",
                name="Standard Indoor / Outdoor Dining",
                location_desc="Main dining room",
                atmosphere="Pleasant resort ambience",
                view="Resort grounds",
                requires_advance_booking=False
            )
        ])

        chef_note = None
        if "Azure" in r.get("name", ""):
            chef_note = "Executive Chef Laurent Moreau sources all seafood daily from local Azure Bay artisanal fishermen at 5:00 AM."
        elif "Jardin" in r.get("name", ""):
            chef_note = "Chef de Cuisine Claire Dupont infuses heirloom herbs grown directly in our courtyard botanical garden."

        venues.append(DiningVenueDetails(
            id=vid,
            name=r.get("name", ""),
            cuisine_type=r.get("cuisine_type", ""),
            dining_style=r.get("dining_style", "Casual"),
            location=r.get("location", ""),
            hours=r.get("hours", {}),
            dress_code=r.get("dress_code", "Resort Casual"),
            reservation_required=r.get("reservation_required", False),
            price_level=r.get("price_level", "$$$"),
            signature_dishes=r.get("signature_dishes", []),
            dietary_options=r.get("dietary_options", []),
            seating_areas=seating,
            room_service_available=r.get("room_service_available", False),
            chef_notes=chef_note
        ))

    return venues
