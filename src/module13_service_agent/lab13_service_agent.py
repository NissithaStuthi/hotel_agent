"""Module 13: Guest Service Request Agent — Lab Execution

Demonstrates:
1. Complete 6-stage service request pipeline:
   Guest Request -> Intent Detection -> Required Information -> Tool Call -> Structured Request -> Confirmation
2. Interactive multi-turn slot filling for missing room numbers
3. Local SQLite database storage and lifecycle updates
4. Automatic ticket code generation and status tracking
"""

import sys
import src.utils.console_display  # Windows UTF-8 support
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.module13_service_agent.service_agent import GuestServiceRequestAgent
from src.module13_service_agent.database import ServiceRequestDatabase
from src.module13_service_agent.models import ServiceRequestStatus


def run_lab13():
    console = Console()
    console.print(Panel.fit(
        "[bold gold1]MODULE 13: GUEST SERVICE REQUEST AGENT[/bold gold1]\n"
        "[italic cyan]Intent Detection, Missing Info Slot-Filling, Tool Calling & SQLite Persistence[/italic cyan]",
        border_style="gold1"
    ))

    # Pipeline diagram
    pipeline_diagram = """
    [bold gold1]Guest Request[/bold gold1]
          ↓
    [bold cyan]Intent Detection[/bold cyan] (Category & Requested Items)
          ↓
    [yellow]Required Information[/yellow] (Verify Room Number & Parameters)
          ↓
    [green]Tool Call[/green] (create_service_request)
          ↓
    [bold magenta]Structured Request[/bold magenta] (Stored in SQLite Database)
          ↓
    [bold white]Confirmation[/bold white] (Chief Concierge Julian with Ticket & Turnaround)
    """
    console.print(Panel(pipeline_diagram, title="Guest Service Pipeline", border_style="cyan"))

    db = ServiceRequestDatabase()
    agent = GuestServiceRequestAgent(db=db)

    # 1. Test Case A: Missing Room Number (Slot filling flow)
    console.print("\n[bold cyan]1. Testing Slot-Filling Flow (Missing Room Number)...[/bold cyan]")
    q1 = "I need two extra towels."
    console.print(f"[bold yellow]Turn 1 Guest:[/bold yellow] \"{q1}\"")
    res1 = agent.process_request(q1, guest_name="Lady Catherine")
    console.print(f"[bold green]Julian:[/bold green] {res1['reply']}")
    console.print(f"  [italic]State: Status='{res1['status']}', Missing Slot='{res1.get('pending_slot')}'[/italic]\n")

    # Turn 2: Guest provides room number
    q2 = "Room 412"
    console.print(f"[bold yellow]Turn 2 Guest:[/bold yellow] \"{q2}\"")
    res2 = agent.process_request(
        q2,
        guest_name="Lady Catherine",
        pending_items=res1.get("pending_items"),
        pending_category=res1.get("pending_category")
    )
    console.print(f"[bold green]Julian:[/bold green]\n{res2['reply']}")
    created_ticket1 = res2["request"].ticket_number if res2.get("request") else "N/A"
    console.print(f"  [bold green]✔ Successfully created ticket:[/bold green] `{created_ticket1}`\n")

    # 2. Test Case B: Housekeeping Request with Room Number
    console.print("[bold cyan]2. Testing Housekeeping Request (Direct Complete Parameters)...[/bold cyan]")
    q3 = "Please arrange housekeeping for Room 204."
    console.print(f"[bold yellow]Guest:[/bold yellow] \"{q3}\"")
    res3 = agent.process_request(q3, guest_name="Lord Harrington")
    console.print(f"[bold green]Julian:[/bold green]\n{res3['reply']}")
    created_ticket2 = res3["request"].ticket_number if res3.get("request") else "N/A"
    console.print(f"  [bold green]✔ Successfully created ticket:[/bold green] `{created_ticket2}`\n")

    # 3. Test Case C: Late Checkout Request
    console.print("[bold cyan]3. Testing Late Checkout Request (Front Desk Extension)...[/bold cyan]")
    q4 = "Can I request a late checkout for Villa 8?"
    console.print(f"[bold yellow]Guest:[/bold yellow] \"{q4}\"")
    res4 = agent.process_request(q4, guest_name="Senator Vance")
    console.print(f"[bold green]Julian:[/bold green]\n{res4['reply']}\n")

    # 4. Test Case D: Querying Status of an Existing Ticket
    console.print(f"[bold cyan]4. Querying Live Ticket Status in Database ({created_ticket1})...[/bold cyan]")
    status_res = agent.check_status(created_ticket1)
    console.print(f"[bold green]Status Lookup:[/bold green]\n{status_res['reply']}\n")

    # 5. Database Records Overview
    console.print("[bold cyan]5. Current Local SQLite Database State (service_requests.db)...[/bold cyan]")
    requests = db.list_requests(limit=10)
    db_table = Table(title="Recent Service Requests in SQLite Database", header_style="bold gold1")
    db_table.add_column("Ticket #", style="cyan")
    db_table.add_column("Room", style="yellow")
    db_table.add_column("Guest Name", style="white")
    db_table.add_column("Category", style="green")
    db_table.add_column("Requested Items", style="white")
    db_table.add_column("Status", style="magenta")
    db_table.add_column("Delivery Time", style="italic")

    for r in requests:
        db_table.add_row(
            r.ticket_number,
            r.room_number,
            r.guest_name or "Guest",
            r.category.value.title(),
            ", ".join(r.requested_items),
            r.status.value.upper(),
            r.estimated_completion_time.split()[-1]
        )
    console.print(db_table)

    stats = db.get_statistics()
    console.print(f"\n[italic]Total tickets in DB: {stats['total_requests']} | Breakdown: {stats['by_category']}[/italic]")
    console.print("\n[bold green]✔ Module 13 Service Request Agent successfully demonstrated![/bold green]\n")


if __name__ == "__main__":
    run_lab13()
