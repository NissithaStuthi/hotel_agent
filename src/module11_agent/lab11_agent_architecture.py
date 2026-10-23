"""Module 11: Concierge Agent Architecture — Lab Execution

Demonstrates:
1. Converting the conversational chatbot into an autonomous agent
2. Agent planning & goal decomposition
3. Tool selection routing across Hotel KB, Hotel Services, and Local Info
4. Multi-turn agent state tracking and thought-action-observation trace
5. Grounded decision making and synthesis
"""

import sys
import src.utils.console_display  # Windows UTF-8 support
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.module11_agent.agent_core import ConciergeAgent
from src.module11_agent.planner import AgentPlanner
from src.module11_agent.models import AgentState


def run_lab11():
    console = Console()
    console.print(Panel.fit(
        "[bold gold1]MODULE 11: CONCIERGE AGENT ARCHITECTURE[/bold gold1]\n"
        "[italic cyan]Converting Chatbot into an Autonomous Agent: Planning, Tool Selection, State & Decisions[/italic cyan]",
        border_style="gold1"
    ))

    # Architecture Diagram
    arch_diagram = """
                [bold gold1]Guest[/bold gold1]
                  ↓
            [bold cyan]Concierge Agent[/bold cyan] (Chief Concierge Julian)
                  ↓
        ┌─────────┼─────────┐
        ↓         ↓         ↓
    [green]Hotel KB[/green]   [yellow]Services[/yellow]   [magenta]Local Info[/magenta]
        ↓         ↓         ↓
        └─────────┼─────────┘
                  ↓
                [bold red]LLM[/bold red]
                  ↓
               [bold white]Response[/bold white]
    """
    console.print(Panel(arch_diagram, title="Autonomous Concierge Agent Architecture", border_style="cyan"))

    # 1. Initialize Concierge Agent
    console.print("\n[bold cyan]1. Initializing Autonomous Concierge Agent...[/bold cyan]")
    agent = ConciergeAgent()
    console.print(f"• Session ID: `{agent.session_id}`")
    console.print("• Persona: Chief Concierge Julian Saint-Claire (Les Clefs d'Or)")
    console.print(f"• Tool Registry: {len(agent.tools.list_tools())} tools loaded\n")

    # 2. Test Multi-turn Deliberation with State & Planning
    test_queries = [
        ("Hotel KB Inquiry", "What is the pet policy at the resort and what are the fees?"),
        ("Services & Action", "Please send two extra plush towels to Room 402."),
        ("Local Info & Proximity", "How far is the Emerald Cove Sea Caves from the hotel and how do we get there?"),
        ("Complex Itinerary Inquiry", "I have one free day tomorrow. Plan something for me.")
    ]

    for category, query in test_queries:
        console.print(f"[bold yellow]▶ Test Case: {category}[/bold yellow]")
        console.print(f"[italic]Guest: \"{query}\"[/italic]")

        turn_res = agent.process_turn(query)

        # Show Plan
        plan_dict = turn_res.get("plan", {})
        console.print(f"  🎯 [bold]Goal:[/bold] {plan_dict.get('goal')}")
        console.print(f"  ⚡ [bold]Complexity:[/bold] {plan_dict.get('complexity')} ({len(plan_dict.get('steps', []))} steps)")

        # Show Tools Executed
        exec_tools = turn_res.get("executed_tools", [])
        if exec_tools:
            t_table = Table(title="Agent Tool Deliberation & Execution", header_style="bold gold1")
            t_table.add_column("Tool", style="cyan")
            t_table.add_column("Arguments", style="white")
            t_table.add_column("Status", style="green")
            t_table.add_column("Summary", style="italic")

            for t in exec_tools:
                t_table.add_row(
                    t["tool"],
                    str(t["args"]),
                    "Success" if t["success"] else "Failed",
                    t["summary"]
                )
            console.print(t_table)

        # Show Response
        console.print(Panel(turn_res["reply"], title="Julian's Response", border_style="gold1"))
        console.print("-" * 75 + "\n")

    console.print("[bold green]✔ Module 11 Agent Architecture successfully demonstrated![/bold green]\n")


if __name__ == "__main__":
    run_lab11()
