"""Module 16: Complaint & Issue Resolution Agent - Lab Runner

Demonstrates complaint intake, severity classification, troubleshooting steps,
automated SQLite ticket dispatch, and managerial escalation.
"""

import src.utils.console_display  # Windows UTF-8 support
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.module16_complaint_agent.complaint_agent import ComplaintResolutionAgent


def run_lab16():
    console = Console()
    console.print(Panel.fit(
        "[bold cyan]🏨 MODULE 16: COMPLAINT & ISSUE RESOLUTION AGENT[/bold cyan]\n"
        "[dim]Intelligent Triage • Troubleshooting KB • Automated SQLite Tickets • MOD Escalation[/dim]",
        border_style="cyan"
    ))

    agent = ComplaintResolutionAgent()

    test_complaints = [
        ("The AC in my room isn't working.", "Suite 504", "Lord Harrington"),
        ("The Wi-Fi in room 312 keeps dropping every two minutes during my Zoom call.", "Room 312", "Dr. Vance"),
        ("Water is leaking from underneath the bathroom vanity in room 204 onto the carpet!", "Room 204", "Elena Rostova"),
        ("There is a loud party in the suite next door at 1:30 AM keeping us awake.", "Suite 410", "Marcus Sterling"),
    ]

    summary_table = Table(title="Complaint Resolution & Triage Summary", border_style="cyan")
    summary_table.add_column("Guest Query", style="bold white", width=30)
    summary_table.add_column("Category", style="yellow")
    summary_table.add_column("Severity", style="bold red")
    summary_table.add_column("Troubleshoot?", style="green")
    summary_table.add_column("Ticket ID", style="cyan")
    summary_table.add_column("Escalation", style="magenta")

    for idx, (query, room, guest) in enumerate(test_complaints, start=1):
        console.print(f"\n[bold yellow]── [Case {idx}] Guest Complaint: \"{query}\" ({room}) ──[/bold yellow]")
        result = agent.process_complaint(query, room_number=room, guest_name=guest)

        summary_table.add_row(
            query,
            result.analysis.detected_category.value,
            result.analysis.detected_severity.value.upper(),
            "Yes" if result.suggested_steps else "No",
            result.service_request_id or "N/A",
            result.analysis.escalation_level.value,
        )

        console.print(f"[bold]Detected Category:[/bold] {result.analysis.detected_category.value}")
        console.print(f"[bold]Assessed Severity:[/bold] [red]{result.analysis.detected_severity.value.upper()}[/red] | [bold]Escalation:[/bold] {result.analysis.escalation_level.value}")
        if result.suggested_steps:
            console.print("[bold green]Suggested In-Room Troubleshooting Steps:[/bold green]")
            for step in result.suggested_steps:
                console.print(f"  • {step}")
        if result.ticket_created:
            console.print(f"[bold cyan]Auto-Dispatched Service Ticket:[/bold cyan] {result.service_request_id}")
        console.print(Panel(result.concierge_response, title=f"Chief Concierge Julian Saint-Claire ({room})", border_style="bright_blue"))

    console.print("\n")
    console.print(summary_table)
    console.print("[bold green]✔ Module 16 Complaint & Issue Resolution Agent completed successfully![/bold green]\n")


if __name__ == "__main__":
    run_lab16()
