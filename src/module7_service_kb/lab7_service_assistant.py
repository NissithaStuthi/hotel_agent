"""Module 7: Hotel Service Knowledge Assistant — Lab Execution & Benchmarking

Demonstrates:
1. Initializing 9 dedicated service collections in ChromaDB
2. Querying each service (Housekeeping, Laundry, Room service, Wi-Fi, Parking, Gym, Pool, Spa, Restaurants)
3. Running retrieval accuracy benchmark and calculating Top-1 and Top-3 accuracy
4. Processing an actionable service request
"""

import sys
import src.utils.console_display  # Windows UTF-8 console support
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.module7_service_kb.models import ServiceCategory
from src.module7_service_kb.service_collections import ServiceCollectionManager
from src.module7_service_kb.service_assistant import HotelServiceAssistant


def run_lab7():
    console = Console()
    console.print(Panel.fit(
        "[bold gold1]MODULE 7: HOTEL SERVICE KNOWLEDGE ASSISTANT[/bold gold1]\n"
        "[italic cyan]Dedicated Service Collections & Retrieval Accuracy Benchmarking[/italic cyan]",
        border_style="gold1"
    ))

    # 1. Initialize Collections Manager
    console.print("\n[bold cyan]1. Initializing 9 Isolated Service Knowledge Collections...[/bold cyan]")
    manager = ServiceCollectionManager()
    
    col_table = Table(title="ChromaDB Dedicated Service Collections", header_style="bold magenta")
    col_table.add_column("Service Category", style="cyan")
    col_table.add_column("Collection Name", style="green")
    col_table.add_column("Indexed Chunks", justify="center")
    
    for cat in manager.CORE_SERVICES:
        col = manager.collections[cat]
        col_table.add_row(cat.value.title(), col.name, str(col.count()))
    console.print(col_table)

    # 2. Querying sample questions across all 9 services
    console.print("\n[bold cyan]2. Testing Inquiries Across All 9 Core Services...[/bold cyan]")
    assistant = HotelServiceAssistant(collection_manager=manager)

    sample_queries = [
        ("Housekeeping", "Can I get extra plush towels and a memory foam pillow sent to Room 402?"),
        ("Laundry", "How quickly can you dry-clean my suit and press a silk shirt? Is there express service?"),
        ("Room Service", "What are your in-room dining breakfast hours, and can I order a Wagyu burger overnight?"),
        ("Wi-Fi", "What is the Wi-Fi password and how many devices can connect?"),
        ("Parking", "How much is overnight valet parking and do you have Tesla EV superchargers?"),
        ("Gym", "What are the fitness center hours, and when is the sunrise oceanfront yoga class?"),
        ("Pool", "What is the water temperature of the cliffside infinity pool and can we rent a private cabana?"),
        ("Spa", "What signature massage do you recommend and is the thalassotherapy circuit included?"),
        ("Restaurants", "What is the dress code and hours for dinner at Azure Breeze Seafood Grill?")
    ]

    for label, query in sample_queries:
        resp = assistant.answer_service_query(query)
        console.print(f"\n[bold yellow]Service Query ({label}):[/bold yellow] [italic]\"{query}\"[/italic]")
        console.print(f"[bold green]Concierge Julian ({resp.category.value.title()}):[/bold green]")
        console.print(f"{resp.answer[:240]}...")
        console.print(f"[dim][Contact: {resp.contact}] | Actionable: {resp.actionable} | Suggested: {', '.join(resp.suggested_actions[:2])}[/dim]")

    # 3. Comprehensive Retrieval Accuracy Benchmark
    console.print("\n[bold cyan]3. Executing Practical Retrieval Accuracy Benchmark across 9 Services...[/bold cyan]")
    eval_results = manager.evaluate_retrieval_accuracy()

    bench_table = Table(title="Retrieval Accuracy Benchmark Results", header_style="bold gold1")
    bench_table.add_column("Service Category", style="cyan")
    bench_table.add_column("Queries Tested", justify="center")
    bench_table.add_column("Routing Acc", justify="center", style="green")
    bench_table.add_column("Top-1 Precision", justify="center", style="yellow")
    bench_table.add_column("Top-3 Precision", justify="center", style="bold green")

    for service_name, stats in eval_results["service_breakdown"].items():
        total = stats["total"]
        if total > 0:
            routing_pct = f"{(stats['correct_routing'] / total) * 100:.0f}%"
            top1_pct = f"{(stats['top1_match'] / total) * 100:.0f}%"
            top3_pct = f"{(stats['top3_match'] / total) * 100:.0f}%"
        else:
            routing_pct, top1_pct, top3_pct = "N/A", "N/A", "N/A"
        bench_table.add_row(service_name.title(), str(total), routing_pct, top1_pct, top3_pct)

    console.print(bench_table)

    console.print(Panel(
        f"[bold white]Overall Benchmark Summary:[/bold white]\n"
        f"• Total Queries Tested: [bold cyan]{eval_results['total_queries_tested']}[/bold cyan]\n"
        f"• Intent Routing Accuracy: [bold green]{eval_results['overall_routing_accuracy'] * 100:.1f}%[/bold green]\n"
        f"• Top-1 Retrieval Precision: [bold yellow]{eval_results['overall_top1_precision'] * 100:.1f}%[/bold yellow]\n"
        f"• Top-3 Grounded Precision: [bold bold green]{eval_results['overall_top3_precision'] * 100:.1f}%[/bold bold green]",
        title="Benchmark Metrics",
        border_style="green"
    ))

    # 4. Actionable Request Logging Test
    console.print("\n[bold cyan]4. Testing Service Request Dispatch...[/bold cyan]")
    action_resp = assistant.answer_service_query(
        "Please send 2 extra bath sheets and dental kit to Room 512 urgently.",
        guest_context={"room_number": "512", "guest_name": "Eleanor Vance"}
    )
    console.print(f"[bold green]Dispatch Logged:[/bold green] {action_resp.actionable}")
    if assistant.logged_requests:
        latest = assistant.logged_requests[-1]
        console.print(f"[dim]Request Details: Category={latest.category.value}, Room={latest.room_number}, Priority={latest.priority}, Status={latest.status}[/dim]")

    console.print("\n[bold green][OK] Module 7 Lab Completed Successfully![/bold green]\n")


if __name__ == "__main__":
    run_lab7()
