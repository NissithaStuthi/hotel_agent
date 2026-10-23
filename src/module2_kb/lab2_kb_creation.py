"""Module 2 Practical Lab: Knowledge Base Creation & Validation

Demonstrates structured data ingestion, Pydantic validation,
and programmatic knowledge querying for the hotel concierge.
"""

from typing import Dict, Any
import src.utils.console_display  # Ensures UTF-8 on Windows
from src.module2_kb.kb_manager import KnowledgeBaseManager


def run_lab2() -> Dict[str, Any]:
    """Runs Module 2 knowledge base creation and validation lab."""
    print("=" * 80)
    print("🏨 MODULE 2: HOTEL KNOWLEDGE BASE CREATION & VERIFICATION")
    print("=" * 80)

    kb = KnowledgeBaseManager()
    stats = kb.get_summary_stats()

    print("\n[PART 1] Knowledge Base Inventory & Statistics:")
    print("-" * 80)
    print(f"  Hotel Entity:                {stats['hotel_name']}")
    print(f"  Room Types Cataloged:        {stats['total_rooms_cataloged']}")
    print(f"  Dining Venues Cataloged:     {stats['total_restaurants']}")
    print(f"  Spa Treatments Cataloged:    {stats['total_spa_treatments']}")
    print(f"  Amenities Cataloged:         {stats['total_amenities']}")
    print(f"  Formal Policies Cataloged:   {stats['total_policies']}")
    print(f"  Local Attractions:           {stats['total_attractions']}")
    print(f"  Transportation Options:      {stats['total_transport_options']}")
    print(f"  Markdown Knowledge Docs:     {stats['total_markdown_documents']}")

    # Verification checks
    assert stats['total_rooms_cataloged'] > 0, "No rooms found!"
    assert stats['total_restaurants'] > 0, "No restaurants found!"
    assert stats['total_policies'] > 0, "No policies found!"
    assert stats['total_markdown_documents'] > 0, "No markdown docs found!"

    print("\n[PART 2] Sample Programmatic Queries:")
    print("-" * 80)

    # 1. Pet-friendly rooms for 4 guests
    pet_rooms = kb.filter_rooms(min_occupancy=4, pet_friendly=True)
    print("\n🐾 Query 1: Pet-friendly rooms accommodating at least 4 guests:")
    for r in pet_rooms:
        print(f"   • {r.name} (${r.base_rate_usd}/night) — Max Occ: {r.max_occupancy} | Bed: {r.bed_configuration}")

    # 2. Restaurants with Gluten-Free options
    gf_dining = kb.filter_restaurants(dietary_option="Gluten-Free")
    print("\n🥗 Query 2: Dining options featuring Gluten-Free selections:")
    for d in gf_dining:
        print(f"   • {d.name} ({d.cuisine_type}) — Hours: {list(d.hours.items())[0]}")

    # 3. Policy search for 'cancellation'
    cancel_policies = kb.find_policy("cancellation")
    print("\n📜 Query 3: Policies matching 'cancellation':")
    for p in cancel_policies:
        print(f"   • [{p.title}] — Strictness: {p.strictness_level}")
        print(f"     Summary: {p.summary}")

    print("\n" + "=" * 80)
    print("✅ Module 2 Lab Completed: All hotel knowledge files created and validated.")
    print("=" * 80)

    return stats


if __name__ == "__main__":
    run_lab2()
