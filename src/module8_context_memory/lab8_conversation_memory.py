"""Module 8: Guest Context & Conversation Memory — Lab Execution

Demonstrates:
1. Multi-turn dialogue tracking
2. Short-term context & coreference resolution:
   Guest: "I want a restaurant for dinner."
   AI: "What type of food do you prefer?"
   Guest: "Italian."
   -> System correctly resolves "Italian" to the dinner restaurant request!
3. Slot filling (cuisine, party size, reservation time)
4. Session state and user preference inspection
"""

import sys
import src.utils.console_display  # Windows UTF-8 console support
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.module8_context_memory.session_state import SessionState
from src.module8_context_memory.contextual_concierge import ContextualConcierge


def run_lab8():
    console = Console()
    console.print(Panel.fit(
        "[bold gold1]MODULE 8: GUEST CONTEXT & CONVERSATION MEMORY[/bold gold1]\n"
        "[italic cyan]Multi-Turn Dialogue Tracking, Coreference & Session State[/italic cyan]",
        border_style="gold1"
    ))

    session = SessionState()
    concierge = ContextualConcierge(session_state=session)

    # Multi-turn test sequence
    conversation_script = [
        "Good afternoon Julian, I am Eleanor Vance staying in Suite 402.",
        "I want a restaurant for dinner.",
        "Italian.",
        "Can you book a table for 2 tomorrow at 7:30 PM?"
    ]

    console.print("\n[bold cyan]1. Executing Multi-Turn Conversational Dialogue...[/bold cyan]\n")

    for idx, user_input in enumerate(conversation_script, 1):
        console.print(f"[bold yellow]Turn {idx} — Guest:[/bold yellow] [italic]\"{user_input}\"[/italic]")
        
        result = concierge.chat(user_input)
        
        # Display resolution indicator if context was used
        if result["context_used"]:
            console.print(f"  [dim cyan]-> [Context Resolved]: \"{result['resolved_query']}\"[/dim cyan]")
        
        console.print(f"[bold green]Julian Saint-Claire:[/bold green]")
        console.print(f"{result['reply']}\n")
        console.print("-" * 75)

    # 2. Inspect Session State & Memory Slots
    console.print("\n[bold cyan]2. Inspecting Active Session State & Context Slots...[/bold cyan]")
    state_dict = session.to_dict()

    state_table = Table(title="Live Session State & Context Slots", header_style="bold gold1")
    state_table.add_column("Property", style="cyan")
    state_table.add_column("Value", style="green")

    state_table.add_row("Session ID", state_dict["session_id"])
    state_table.add_row("Total Turns Completed", str(state_dict["total_turns"]))
    state_table.add_row("Active Intent", str(state_dict["active_intent"]))
    state_table.add_row("Active Domain", str(state_dict["active_domain"]))
    
    # Context slots
    for k, v in state_dict["context_slots"].items():
        state_table.add_row(f"Slot: {k}", str(v))

    console.print(state_table)

    # 3. Inspect Guest Profile & Learned Preferences
    console.print("\n[bold cyan]3. Inspecting Learned Guest Profile & Preferences...[/bold cyan]")
    pref_table = Table(title="Guest Profile Memory", header_style="bold magenta")
    pref_table.add_column("Profile Field", style="cyan")
    pref_table.add_column("Learned Value", style="bold yellow")

    prefs = state_dict["preferences"]
    pref_table.add_row("Guest Name", str(prefs["guest_name"]))
    pref_table.add_row("Room Number", str(prefs["room_number"]))
    pref_table.add_row("Party Type", str(prefs["party_type"]))
    pref_table.add_row("Dietary & Cuisine Preferences", ", ".join(prefs["dietary"]) if prefs["dietary"] else "None")
    pref_table.add_row("Special Occasions", ", ".join(prefs["special_occasions"]) if prefs["special_occasions"] else "None")

    console.print(pref_table)

    console.print("\n[bold green][OK] Module 8 Lab Completed Successfully![/bold green]\n")


if __name__ == "__main__":
    run_lab8()
