"""Module 12: Tool Calling — Lab Execution

Demonstrates:
1. Local Python tools with structured JSON Schema definitions
2. Central Tool Registry managing invocable agent tools
3. Allowing the LLM to decide which tool is required
4. Tool parameter extraction and execution returning structured ToolResults
"""

import sys
import src.utils.console_display  # Windows UTF-8 support
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.module12_tool_calling.tools import ToolRegistry
from src.module12_tool_calling.tool_caller import LLMToolDispatcher


def run_lab12():
    console = Console()
    console.print(Panel.fit(
        "[bold gold1]MODULE 12: AGENT TOOL CALLING[/bold gold1]\n"
        "[italic cyan]Local Invocable Python Tools, Schemas & LLM Autonomous Tool Selection[/italic cyan]",
        border_style="gold1"
    ))

    # 1. Inspect Invocable Tools
    console.print("\n[bold cyan]1. Invocable Local Python Tools Registry...[/bold cyan]")
    registry = ToolRegistry()
    tools = registry.list_tools()

    tool_table = Table(title="Registered Agent Tools", header_style="bold gold1")
    tool_table.add_column("Tool Name", style="cyan")
    tool_table.add_column("Description", style="white")
    tool_table.add_column("Required Parameters", style="yellow")

    for t in tools:
        props = t.parameters.get("properties", {})
        req = t.parameters.get("required", [])
        params_str = ", ".join(f"{p}*" if p in req else p for p in props.keys())
        tool_table.add_row(t.name, t.description, params_str or "(None)")

    console.print(tool_table)

    # 2. Test LLM Tool Decision Across Diverse Inquiries
    console.print("\n[bold cyan]2. Testing LLM Decision Making & Tool Dispatch...[/bold cyan]")
    dispatcher = LLMToolDispatcher(registry=registry)

    benchmark_queries = [
        ("Room Specs", "What are the features and rates for the Presidential Villa?"),
        ("Dining Hours & Menu", "What time does dinner start at Azure Breeze and what is their signature dish?"),
        ("Policy Question", "Can we bring our golden retriever to the resort and what is the policy?"),
        ("Attractions Discovery", "What natural sights and sea caves are nearby?"),
        ("Distance & Transit", "How far is the Historic Old Town Citadel from our hotel?"),
        ("Service Request", "Please send two extra towels to Room 314."),
        ("Hotel Services", "What are the operating hours and treatments at the spa?")
    ]

    for label, query in benchmark_queries:
        console.print(f"[bold yellow]▶ Scenario: {label}[/bold yellow]")
        console.print(f"[italic]Guest Query: \"{query}\"[/italic]")

        tool_call, tool_result = dispatcher.execute_query(query)

        if tool_call:
            console.print(f"  ⚡ [bold green]LLM Decided Tool:[/bold green] `{tool_call.tool_name}`")
            console.print(f"  📋 [bold]Arguments Extracted:[/bold] {tool_call.arguments}")
            console.print(f"  💡 [bold]Rationale:[/bold] {tool_call.rationale}")

        if tool_result:
            status_style = "green" if tool_result.success else "red"
            console.print(f"  [{status_style}]Execution Status: {tool_result.summary()} ({tool_result.execution_time_ms} ms)[/{status_style}]")
            
            # Show snippet of returned data
            data = tool_result.data
            if isinstance(data, list) and data:
                snippet = f"Returned {len(data)} records. First record: {data[0].get('name', data[0].get('title', 'Record'))}"
            elif isinstance(data, dict):
                snippet = f"Keys: {list(data.keys())[:4]}..."
            else:
                snippet = str(data)[:100]
            console.print(f"  📦 [italic]Data Payload: {snippet}[/italic]")

        console.print("-" * 75 + "\n")

    console.print("[bold green]✔ Module 12 Tool Calling successfully demonstrated![/bold green]\n")


if __name__ == "__main__":
    run_lab12()
