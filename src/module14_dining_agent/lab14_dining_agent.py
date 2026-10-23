"""Module 14: Restaurant & Dining Agent — Lab Execution

Demonstrates:
1. Specialized restaurant capability covering 6 essential dining topics:
   - Restaurant timings
   - Cuisine styles & concepts
   - Menu information & signature dishes
   - Dietary options (vegan, gluten-free, halal-friendly, allergens)
   - Seating options (cliffside terrace, botanical garden, cellar, cabanas)
   - Room service schedule and 24/7 ordering
2. Advanced multi-criteria dining recommendations tailored to guest preferences
3. Table reservation creation with unique confirmation code tracking
"""

import sys
import src.utils.console_display  # Windows UTF-8 support
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.module14_dining_agent.dining_agent import RestaurantDiningAgent
from src.module14_dining_agent.models import DiningPreferences


def run_lab14():
    console = Console()
    console.print(Panel.fit(
        "[bold gold1]MODULE 14: RESTAURANT & DINING AGENT[/bold gold1]\n"
        "[italic cyan]Specialized Dining Intelligence: Hours, Menus, Dietary, Seating, Room Service & Reservations[/italic cyan]",
        border_style="gold1"
    ))

    agent = RestaurantDiningAgent()

    # 1. Overview of Dining Venues
    console.print("\n[bold cyan]1. Cataloged Resort Dining Collection...[/bold cyan]")
    v_table = Table(title="Resort Dining Venues & Concepts", header_style="bold gold1")
    v_table.add_column("Venue Name", style="cyan")
    v_table.add_column("Cuisine", style="green")
    v_table.add_column("Style", style="white")
    v_table.add_column("Price", style="yellow")
    v_table.add_column("Key Seating Section", style="italic")

    for v in agent.venues:
        seat_name = v.seating_areas[0].name if v.seating_areas else "Main Dining"
        v_table.add_row(v.name, v.cuisine_type, v.dining_style, v.price_level, seat_name)
    console.print(v_table)

    # 2. Benchmark 6 Core Dining Inquiries
    console.print("\n[bold cyan]2. Testing 6 Specialized Dining Query Dimensions...[/bold cyan]")

    core_queries = [
        ("1. Timings & Hours", "What time does dinner start and end at Azure Breeze?"),
        ("2. Cuisine & Concept", "What cuisine is served at Le Jardin French Bistro?"),
        ("3. Menu & Signature Dishes", "What signature dishes do you recommend at Azure Breeze?"),
        ("4. Dietary Accommodations", "What options do you offer for vegan and gluten-free guests?"),
        ("5. Seating & Atmosphere", "What seating options with ocean sunset views are available?"),
        ("6. In-Room Dining (Room Service)", "Can we order room service late at night and what is on the menu?")
    ]

    for label, query in core_queries:
        console.print(f"[bold yellow]▶ {label}[/bold yellow]")
        console.print(f"[italic]Guest: \"{query}\"[/italic]")
        ans = agent.answer_dining_query(query)
        console.print(Panel(ans["reply"], title="Julian's Dining Advice", border_style="gold1"))
        console.print("-" * 75 + "\n")

    # 3. Advanced Recommendation based on Guest Preferences
    console.print("[bold cyan]3. Advanced Preference-Based Dining Recommendation...[/bold cyan]")
    pref = DiningPreferences(
        party_size=2,
        atmosphere_preference="romantic",
        dietary_restrictions=["Gluten-Free"],
        cuisine="Seafood",
        preferred_seating="Cliffside Sunset Terrace"
    )
    console.print(f"[italic]Guest Profile: 2 Guests, Romantic Anniversary Vibe, Gluten-Free, Seafood Preference[/italic]")
    rec_res = agent.recommend_dining(pref)
    console.print(Panel(rec_res["reply"], title="Tailored Recommendation", border_style="cyan"))

    # 4. Table Reservation Booking Flow
    console.print("\n[bold cyan]4. Booking a Confirmed Table Reservation...[/bold cyan]")
    booking_q = "Please book a table for 2 tomorrow at 7:30 PM at Azure Breeze on the cliffside terrace."
    console.print(f"[italic]Guest Request: \"{booking_q}\"[/italic]")
    book_res = agent.answer_dining_query(booking_q)
    console.print(Panel(book_res["reply"], title="Table Reservation Confirmation", border_style="green"))

    console.print("[bold green]✔ Module 14 Restaurant & Dining Agent successfully demonstrated![/bold green]\n")


if __name__ == "__main__":
    run_lab14()
