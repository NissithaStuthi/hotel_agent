"""Module 17: Multi-Agent Concierge System - Lab Runner

Demonstrates specialized agent routing, compound query decomposition,
multi-agent task execution, and unified Clefs d'Or concierge synthesis.
"""

import src.utils.console_display  # Windows UTF-8 support
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.module17_multi_agent.supervisor import MultiAgentConciergeSupervisor


def run_lab17():
    console = Console()
    console.print(Panel.fit(
        "[bold magenta]🏨 MODULE 17: MULTI-AGENT CONCIERGE SYSTEM[/bold magenta]\n"
        "[italic cyan]Supervisor Agent • 6 Specialized Sub-Agents • Compound Decomposition • Unified Synthesis[/italic cyan]",
        border_style="magenta"
    ))

    # Architectural flow banner
    arch_flow = """
                  [bold gold1]Concierge Agent (Supervisor)[/bold gold1]
                                 │
         ┌───────────────┬───────┴───────┬───────────────┐
         ▼               ▼               ▼               ▼
    [cyan]Hotel Agent[/cyan]    [yellow]Dining Agent[/yellow]   [green]Travel Agent[/green]   [magenta]Service Agent[/magenta]
         │               │               │               │
         └───────┬───────┴───────┬───────┴───────┬───────┘
                 ▼                               ▼
            [blue]Local Agent[/blue]                    [red]Complaint Agent[/red]
    """
    console.print(Panel(arch_flow, title="Multi-Agent Hierarchy", border_style="bright_blue"))

    supervisor = MultiAgentConciergeSupervisor()

    test_queries = [
        ("What time is check-in and check-out tomorrow?", "Suite 102", "Lady Carlisle", "Single-Domain Hotel Knowledge"),
        ("What are the vegetarian and gluten-free dinner options at Azure Breeze?", "Room 304", "Mr. Sterling", "Single-Domain Dining"),
        ("I have one free day tomorrow. Plan something for me.", "Penthouse 901", "Senator Brooks", "Single-Domain Travel Itinerary"),
        (
            "The AC in my room isn't working, also please arrange two extra bath towels and book a romantic dinner table tonight at 7:30 PM.",
            "Suite 402",
            "Duchess of Devonshire",
            "Compound Multi-Agent Request (Complaint + Service + Dining)"
        ),
    ]

    summary_table = Table(title="Multi-Agent Orchestration Log", border_style="magenta")
    summary_table.add_column("Query Type", style="bold white", width=22)
    summary_table.add_column("Primary Role", style="yellow")
    summary_table.add_column("Collaborating Roles", style="cyan")
    summary_table.add_column("Tasks", style="bold green", justify="center")
    summary_table.add_column("Actions Dispatched", style="magenta")

    for idx, (query, room, guest, label) in enumerate(test_queries, start=1):
        console.print(f"\n[bold yellow]── [Test Case {idx}] {label} ──[/bold yellow]")
        console.print(f"[bold white]Guest ({guest}, {room}):[/bold white] \"{query}\"")

        response = supervisor.process_query(query, room_number=room, guest_name=guest)
        routing = response.routing_decision

        collab_str = ", ".join([r.value for r in routing.collaborating_roles]) if routing.collaborating_roles else "None (Direct)"
        summary_table.add_row(
            label[:22],
            routing.primary_role.value,
            collab_str,
            str(len(response.sub_agent_results)),
            str(response.total_actions_dispatched),
        )

        console.print(f"[bold cyan]Routing Decision:[/bold cyan] {routing.reasoning}")
        console.print(f"[bold]Specialized Agents Engaged:[/bold] {len(response.sub_agent_results)}")
        for sub in response.sub_agent_results:
            console.print(f"  • [bold]{sub.agent_name}[/bold] ({sub.execution_time_ms:.1f}ms) — Actions: {sub.actions_taken or ['Answered inquiry']}")

        console.print(Panel(response.unified_response, title=f"Chief Concierge Julian Saint-Claire ({room})", border_style="bright_magenta"))

    console.print("\n")
    console.print(summary_table)
    console.print("[bold green]✔ Module 17 Multi-Agent Concierge System completed successfully![/bold green]\n")


if __name__ == "__main__":
    run_lab17()
