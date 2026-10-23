"""Module 15: Travel & Itinerary Planning Agent — Lab Execution

Demonstrates:
1. Advanced agentic multi-stage itinerary generation:
   Guest Preferences -> Available Time -> Attraction Retrieval -> Distance Calculation -> Restaurant Recommendation -> Schedule Generation -> Final Itinerary
2. Full 12-hour day trip synthesis from natural language ("I have one free day tomorrow. Plan something for me.")
3. Proximity-aware routing, transit coordination, and meal pairings
4. Chronological timeline generation with curator tips
"""

import sys
import src.utils.console_display  # Windows UTF-8 support
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.module15_itinerary_agent.itinerary_planner import TravelItineraryAgent
from src.module15_itinerary_agent.models import GuestItineraryProfile, ItineraryTheme, PacePreference


def run_lab15():
    console = Console()
    console.print(Panel.fit(
        "[bold gold1]MODULE 15: TRAVEL & ITINERARY PLANNING AGENT[/bold gold1]\n"
        "[italic cyan]Advanced Multi-Stage Agentic Synthesis: Sights, Routing, Dining & Chronological Schedules[/italic cyan]",
        border_style="gold1"
    ))

    # Pipeline diagram
    pipeline_diag = """
    [bold gold1]Guest: \"I have one free day tomorrow. Plan something for me.\"[/bold gold1]
           ↓
    [cyan]Guest Preferences[/cyan] (Romantic Coastal, Balanced Pace, Fine Gastronomy)
           ↓
    [yellow]Available Time[/yellow] (Full Day: 12 Hours, 9:00 AM – 9:30 PM)
           ↓
    [green]Attraction Retrieval[/green] (Emerald Cove Caves, Citadel, Artisan Markets)
           ↓
    [magenta]Distance Calculation[/magenta] (Sequenced Route: 14.2 km Total Commute)
           ↓
    [blue]Restaurant Recommendation[/blue] (Trattoria Del Porto Lunch & Azure Breeze Sunset Dinner)
           ↓
    [bold cyan]Schedule Generation[/bold cyan] (Chronological 5-Stop Timeline with Transit Buffers)
           ↓
    [bold white]Final Itinerary[/bold white] (Chief Concierge Julian Bespoke Presentation)
    """
    console.print(Panel(pipeline_diag, title="7-Stage Itinerary Planning Architecture", border_style="cyan"))

    agent = TravelItineraryAgent()

    # 1. Primary Scenario: Free Day Request
    console.print("\n[bold cyan]1. Executing Primary Scenario: 'I have one free day tomorrow. Plan something for me.'[/bold cyan]")
    user_query = "I have one free day tomorrow. Plan something for me."
    console.print(f"[bold yellow]Guest Input:[/bold yellow] \"{user_query}\"\n")

    itinerary, pipeline_log = agent.plan_day(user_query)

    # Display Stage-by-Stage Deliberation Log
    stage_table = Table(title="Agent Pipeline Deliberation Trace", header_style="bold gold1")
    stage_table.add_column("Stage", justify="center", style="cyan")
    stage_table.add_column("Pipeline Phase", style="white")
    stage_table.add_column("Agent Action & Output Details", style="green")

    for s in pipeline_log:
        stage_table.add_row(f"Stage {s['stage']}", s["name"], s["details"])
    console.print(stage_table)

    # Display Chronological Itinerary
    console.print(f"\n[bold gold1]🌅 {itinerary.title}[/bold gold1]")
    console.print(f"[italic]{itinerary.summary}[/italic]\n")

    itin_table = Table(title=f"Chronological Timeline ({itinerary.total_duration_hours:.0f} Hours • {itinerary.total_distance_km} km)", header_style="bold gold1")
    itin_table.add_column("Time Slot", style="cyan")
    itin_table.add_column("Stop & Venue", style="gold1")
    itin_table.add_column("Type", style="yellow")
    itin_table.add_column("Activity Description", style="white")
    itin_table.add_column("Transit / Distance", style="green")
    itin_table.add_column("Concierge Tip", style="italic")

    for stop in itinerary.stops:
        transit_desc = f"{stop.transit_mode} ({stop.distance_from_prev_km} km)" if stop.stop_number > 1 else stop.transit_mode
        itin_table.add_row(
            stop.time_slot,
            f"#{stop.stop_number} {stop.venue_name}",
            stop.category.title(),
            stop.activity_description,
            transit_desc,
            stop.curator_tip[:55] + "..." if len(stop.curator_tip) > 55 else stop.curator_tip
        )
    console.print(itin_table)

    console.print(f"\n🚗 [bold]Transit Logistics:[/bold] {itinerary.transit_advice}")
    console.print(f"🎫 [bold]VIP Bookings:[/bold] {itinerary.booking_instructions}")
    console.print("-" * 75 + "\n")

    # 2. Secondary Scenario: Family Exploration Day
    console.print("[bold cyan]2. Testing Theme Tailoring: Family Marine Discovery Day...[/bold cyan]")
    fam_profile = GuestItineraryProfile(
        theme=ItineraryTheme.FAMILY_COASTAL,
        party_type="family_with_children",
        party_size=4,
        pace=PacePreference.RELAXED,
        available_hours=8.0,
        start_time="10:00 AM",
        end_time="6:00 PM"
    )
    fam_itin, _ = agent.plan_day("We are traveling with two young kids and want a relaxed ocean day", custom_profile=fam_profile)
    console.print(f"• Generated: [bold gold1]{fam_itin.title}[/bold gold1]")
    console.print(f"• Target: {fam_itin.target_audience} | Stops: {len(fam_itin.stops)} family-friendly venues")
    console.print(f"• First stop: {fam_itin.stops[0].venue_name} ({fam_itin.stops[0].time_slot})")

    console.print("\n[bold green]✔ Module 15 Travel & Itinerary Planning Agent successfully demonstrated![/bold green]\n")


if __name__ == "__main__":
    run_lab15()
