"""Module 10: Local Destination Assistant — Lab Execution

Demonstrates:
1. Local destination knowledge base spanning 6 core topics:
   - Attractions
   - Restaurants
   - Shopping
   - Transportation
   - Tourist locations
   - Activities
2. Vector semantic search across attractions & destinations
3. Category-filtered and distance-constrained discovery
4. Curated full-day regional itinerary generation
"""

import sys
import src.utils.console_display  # Windows UTF-8 console support
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.module10_destination.models import DestinationCategory
from src.module10_destination.destination_search import DestinationSemanticSearch
from src.module10_destination.destination_assistant import LocalDestinationAssistant


def run_lab10():
    console = Console()
    console.print(Panel.fit(
        "[bold gold1]MODULE 10: LOCAL DESTINATION ASSISTANT[/bold gold1]\n"
        "[italic cyan]Expanding Beyond the Hotel: Attractions, Dining, Shopping, Transit & Activities[/italic cyan]",
        border_style="gold1"
    ))

    # 1. Initialize Destination Knowledge Base
    console.print("\n[bold cyan]1. Initializing Local Destination Knowledge Base...[/bold cyan]")
    search_engine = DestinationSemanticSearch()
    assistant = LocalDestinationAssistant(search_engine=search_engine)

    cat_table = Table(title="Destination Catalog Breakdown by Topic", header_style="bold gold1")
    cat_table.add_column("Destination Topic", style="cyan")
    cat_table.add_column("Indexed Venues / Services", justify="center", style="green")
    cat_table.add_column("Example Destination Item", style="italic")

    for cat in DestinationCategory:
        items = search_engine.get_by_category(cat)
        example_name = items[0].name if items else "None"
        cat_table.add_row(cat.value.replace("_", " ").title(), str(len(items)), example_name)

    console.print(cat_table)

    # 2. Semantic Search Across Attractions & Destination Topics
    console.print("\n[bold cyan]2. Testing Semantic Search Queries (without exact keyword match)...[/bold cyan]")

    test_queries = [
        ("Attractions", "glowing ocean cave with crystal water for morning exploration", DestinationCategory.ATTRACTIONS),
        ("Shopping", "where can I buy custom bespoke perfumes and local ceramic crafts?", DestinationCategory.SHOPPING),
        ("Dining", "harbor-side authentic Italian trattoria with handmade pasta and fresh seafood", DestinationCategory.RESTAURANTS),
        ("Transportation", "how can we take a boat or shuttle to get around the marina and island?", DestinationCategory.TRANSPORTATION),
        ("Tourist Locations", "dramatic cliffside ocean lookout with sunset benches", DestinationCategory.TOURIST_LOCATIONS),
        ("Activities", "sailing catamaran cruise with champagne and snorkeling", DestinationCategory.ACTIVITIES)
    ]

    for topic_label, query, cat in test_queries:
        search_res = search_engine.search(query=query, category=cat, top_k=2)
        console.print(f"\n[bold yellow]Semantic Query ({topic_label}):[/bold yellow] [italic]\"{query}\"[/italic]")
        
        for idx, res in enumerate(search_res.results, 1):
            it = res.item
            console.print(
                f"  [bold green]#{idx} {it.name}[/bold green] "
                f"[dim]({it.distance_km} km away | ~{it.travel_time_minutes} mins | Similarity: {res.similarity_score:.2f})[/dim]\n"
                f"     [dim white]Highlights: {', '.join(it.highlights[:3])}[/dim white]\n"
                f"     [dim yellow]Transit: {', '.join(it.transit_options)}[/dim yellow]"
            )

    # 3. Concierge Grounded Answer
    console.print("\n[bold cyan]3. Testing Concierge Julian's Grounded Regional Advice...[/bold cyan]")
    concierge_resp = assistant.answer_destination_query(
        "We would love to visit historic castles and shop for handmade crafts in the late afternoon. What do you advise?"
    )
    console.print(Panel(
        concierge_resp["answer"],
        title="Julian's Destination Advice",
        border_style="gold1"
    ))

    # 4. Curated Full-Day Itinerary Planning
    console.print("\n[bold cyan]4. Generating Curated Full-Day Regional Odyssey Itinerary...[/bold cyan]")
    itinerary = assistant.create_curated_itinerary()

    itin_table = Table(title=f"Curated Itinerary: {itinerary.title}", header_style="bold magenta")
    itin_table.add_column("Time Window", style="cyan", justify="center")
    itin_table.add_column("Destination Stop", style="bold green")
    itin_table.add_column("Activity Description", style="white")
    itin_table.add_column("Transit Guidance", style="yellow")

    for stop in itinerary.stops:
        itin_table.add_row(
            stop.time_slot,
            stop.item.name,
            stop.activity_description,
            stop.transit_guidance
        )

    console.print(itin_table)
    console.print(f"[dim]Theme: {itinerary.theme} | Duration: {itinerary.total_duration_hours} hours[/dim]")
    console.print(f"[bold cyan]Concierge Note:[/bold cyan] {itinerary.concierge_notes}")

    console.print("\n[bold green][OK] Module 10 Lab Completed Successfully![/bold green]\n")


if __name__ == "__main__":
    run_lab10()
