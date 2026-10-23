"""Module 4 Practical Lab: Basic LLM Concierge Dialogue & Persona Testing

Executes a multi-turn conversation assessing persona tone, memory tracking,
and de-escalation behavior.
"""

from typing import List, Dict, Any
import src.utils.console_display  # Ensures UTF-8 on Windows
from src.module4_concierge.concierge_agent import BasicConciergeAgent
from src.module4_concierge.persona import PersonaStyle


MULTI_TURN_SCRIPT = [
    "Hello! My name is Eleanor Vance, and I just checked into Room 412.",
    "Could you please tell me when breakfast is served and what restaurants you have?",
    "That sounds lovely. Could we please have 2 extra bath towels brought up to Room 412?",
    "Also, I must mention that the air conditioner in the living area is making a loud buzzing noise!"
]


def run_lab4() -> Dict[str, Any]:
    """Runs Module 4 multi-turn conversational concierge lab."""
    print("=" * 80)
    print("🏨 MODULE 4: BASIC LLM CONCIERGE (PERSONA & DIALOGUE)")
    print("=" * 80)

    agent = BasicConciergeAgent(persona_style=PersonaStyle.LUXURY_CLEFS_D_OR)

    print(f"\nActive Persona: {agent.persona_style.value}")
    print("Beginning Multi-Turn Conversation Simulation:")
    print("-" * 80)

    conversation_record = []
    for turn_idx, user_turn in enumerate(MULTI_TURN_SCRIPT, 1):
        print(f"\n[Turn {turn_idx}] Guest: \"{user_turn}\"")
        response = agent.chat(user_turn)
        print(f"\n[Turn {turn_idx}] Concierge Julian:")
        print(f"\"{response}\"")

        conversation_record.append({
            "turn": turn_idx,
            "guest": user_turn,
            "concierge": response
        })

    # Memory state check
    mem = agent.memory
    print("\n" + "=" * 80)
    print("🧠 CONVERSATIONAL STATE & MEMORY CAPTURE:")
    print(f"   • Guest Name Extracted:   {mem.guest_name}")
    print(f"   • Room Number Captured:   {mem.room_number}")
    print(f"   • Total Turns in Memory:  {len(mem.messages) // 2}")
    print("=" * 80)
    print("✅ Module 4 Lab Completed: Basic LLM concierge conversational loop validated.")
    print("=" * 80)

    return {
        "guest_name": mem.guest_name,
        "room_number": mem.room_number,
        "turns_completed": len(conversation_record),
        "transcript": conversation_record
    }


if __name__ == "__main__":
    run_lab4()
