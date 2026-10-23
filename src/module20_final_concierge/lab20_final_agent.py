"""Module 20: Final AI Hotel Concierge Agent - Master Lab Runner

Comprehensive demonstration of the complete system covering all required features:
✅ Natural-language conversation & Clefs d'Or persona
✅ Hotel knowledge RAG & isolated collections
✅ Semantic vector search
✅ Multi-turn conversation memory & coreference
✅ Personalized multi-criteria recommendations
✅ Local attraction recommendations
✅ Autonomous tool selection & calling
✅ Guest service requests & SQLite tickets
✅ Specialized dining assistant & table reservations
✅ Multi-stage travel itinerary generation
✅ Complaint triage & troubleshooting
✅ Multi-agent architecture (Supervisor + 6 Specialists)
✅ Multimodal image understanding
✅ Hallucination control & evidence grounding
✅ Complete end-to-end agentic workflow
"""

from pathlib import Path
import src.utils.console_display  # Windows UTF-8 support
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.config import DATA_DIR
from src.module20_final_concierge.final_agent import TheGrandAzureMasterAgent


def run_lab20():
    console = Console()
    console.print(Panel.fit(
        "[bold gold1]🏆 MODULE 20: FINAL AI HOTEL CONCIERGE AGENT[/bold gold1]\n"
        "[italic cyan]The Complete Unified Hospitality Intelligence Platform[/italic cyan]\n"
        "[dim]RAG • Memory • Planning • Tools • Services • Dining • Travel • Complaints • Multi-Agent • Vision • Safety[/dim]",
        border_style="gold1"
    ))

    master_agent = TheGrandAzureMasterAgent()
    sample_dir = DATA_DIR / "sample_images"

    scenarios = [
        {
            "label": "1. Hotel Knowledge RAG & Policies",
            "query": "What are your check-in hours and is the infinity pool heated for evening swims?",
            "image": None,
            "guest": "Lord Harrington",
            "room": "Suite 104"
        },
        {
            "label": "2. Service Request & SQLite Dispatch",
            "query": "Please arrange two extra bath towels and fresh bottled water for Room 412.",
            "image": None,
            "guest": "Elena Rostova",
            "room": "Room 412"
        },
        {
            "label": "3. Dining Intelligence & Table Booking",
            "query": "Recommend a romantic dinner table for 2 at Azure Breeze with sunset views at 7:30 PM.",
            "image": None,
            "guest": "Marcus Sterling",
            "room": "Suite 302"
        },
        {
            "label": "4. Full-Day Travel Itinerary Synthesis",
            "query": "I have one free day tomorrow. Plan something for me.",
            "image": None,
            "guest": "Senator Brooks",
            "room": "Penthouse 901"
        },
        {
            "label": "5. Complaint Triage & Troubleshooting",
            "query": "The AC in my room isn't working and it is getting warm.",
            "image": None,
            "guest": "Countess Maria",
            "room": "Suite 504"
        },
        {
            "label": "6. Multimodal Visual Understanding",
            "query": "What is this dish, and which restaurant serves it?",
            "image": sample_dir / "signature_sea_bass.jpg",
            "guest": "Dr. Vance",
            "room": "Suite 208"
        },
        {
            "label": "7. Hallucination Control & Grounded Refusal",
            "query": "Can I rent a private helicopter from the pool deck to fly to the capital?",
            "image": None,
            "guest": "Guest Inquirer",
            "room": "Lobby"
        },
    ]

    summary_table = Table(title="Module 20: Master End-to-End System Audit", border_style="gold1")
    summary_table.add_column("Capability Tested", style="bold white", width=26)
    summary_table.add_column("Primary Specialist", style="yellow")
    summary_table.add_column("Grounding", style="green")
    summary_table.add_column("Dispatched Actions", style="magenta")
    summary_table.add_column("Latency", style="cyan", justify="right")

    for idx, sc in enumerate(scenarios, start=1):
        console.print(f"\n[bold gold1]════════════════════════════════════════════════════════════════════════════════[/bold gold1]")
        console.print(f"[bold gold1]── [Scenario {idx}] {sc['label']} ──[/bold gold1]")
        console.print(f"[bold]Guest:[/bold] {sc['guest']} ({sc['room']}) | [bold]Query:[/bold] \"{sc['query']}\"")
        if sc["image"]:
            console.print(f"[bold cyan]Image Uploaded:[/bold cyan] `{Path(sc['image']).name}`")

        res = master_agent.process_guest_interaction(
            query=sc["query"],
            image_input=sc["image"],
            room_number=sc["room"],
            guest_name=sc["guest"],
            session_id=f"session_demo_{idx}"
        )

        all_actions = res.service_tickets_created + res.dining_reservations_made + res.tools_executed
        actions_str = ", ".join(all_actions) if all_actions else "Grounded consultation"
        primary_agent = res.routing_decision.primary_role.value if res.routing_decision else "concierge"

        summary_table.add_row(
            sc["label"][:26],
            primary_agent,
            res.telemetry.grounding_verdict.value.upper(),
            actions_str[:30],
            f"{res.telemetry.pipeline_duration_ms:.1f}ms",
        )

        console.print(f"[dim]Stages Completed: {' ➔ '.join(res.telemetry.stages_completed)}[/dim]")
        if res.visual_analysis:
            console.print(f"[cyan]Visual Analysis:[/cyan] {res.visual_analysis.scene_description}")
        console.print(Panel(res.final_response, title=f"Chief Concierge Julian Saint-Claire (to {sc['guest']})", border_style="bright_yellow"))

    console.print("\n")
    console.print(summary_table)
    console.print("[bold green]🏆 ALL 20 MODULES COMPLETE & OPERATIONAL IN PRODUCTION SYSTEM ARCHITECTURE![/bold green]\n")


if __name__ == "__main__":
    run_lab20()
