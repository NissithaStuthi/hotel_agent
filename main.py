"""🏨 AI Hotel Concierge Agent — Master Lab & Interactive CLI Runner

Usage:
    python main.py --module 1       # Run Module 1 (Taxonomy & Intro)
    python main.py --module 2       # Run Module 2 (Knowledge Base Creation)
    python main.py --module 3       # Run Module 3 (Intent Classification)
    python main.py --module 4       # Run Module 4 (Basic Conversational Agent)
    python main.py --module 5       # Run Module 5 (Grounded RAG Pipeline)
    python main.py --module 6       # Run Module 6 (Semantic Hotel Search)
    python main.py --module 7       # Run Module 7 (Hotel Service Knowledge Assistant)
    python main.py --module 8       # Run Module 8 (Guest Context & Conversation Memory)
    python main.py --module 9       # Run Module 9 (Personalized Recommendations)
    python main.py --module 10      # Run Module 10 (Local Destination Assistant)
    python main.py --module 11      # Run Module 11 (Concierge Agent Architecture)
    python main.py --module 12      # Run Module 12 (Tool Calling & Registry)
    python main.py --module 13      # Run Module 13 (Guest Service Request Agent)
    python main.py --module 14      # Run Module 14 (Restaurant & Dining Agent)
    python main.py --module 15      # Run Module 15 (Travel & Itinerary Planning Agent)
    python main.py --module 16      # Run Module 16 (Complaint & Issue Resolution Agent)
    python main.py --module 17      # Run Module 17 (Multi-Agent Concierge System)
    python main.py --module 18      # Run Module 18 (Multimodal Concierge Agent)
    python main.py --module 19      # Run Module 19 (Safety, Validation & Hallucination Control)
    python main.py --module 20      # Run Module 20 (Final AI Hotel Concierge Master Agent)
    python main.py --all            # Run all 20 modules sequentially
    python main.py --chat           # Interactive live chat with Master Concierge Agent Julian
"""

import sys
import argparse
import re
import src.utils.console_display  # Configures UTF-8 encoding for Windows console

from src.module1_intro.lab1_analysis import run_lab1
from src.module2_kb.lab2_kb_creation import run_lab2
from src.module3_classifier.lab3_classification import run_lab3
from src.module4_concierge.lab4_basic_agent import run_lab4
from src.module5_rag.lab5_rag_concierge import run_lab5
from src.module6_semantic_search.semantic_search import run_lab6
from src.module7_service_kb.lab7_service_assistant import run_lab7
from src.module8_context_memory.lab8_conversation_memory import run_lab8
from src.module9_recommendations.lab9_recommendations import run_lab9
from src.module10_destination.lab10_destination import run_lab10
from src.module11_agent.lab11_agent_architecture import run_lab11
from src.module12_tool_calling.lab12_tool_calling import run_lab12
from src.module13_service_agent.lab13_service_agent import run_lab13
from src.module14_dining_agent.lab14_dining_agent import run_lab14
from src.module15_itinerary_agent.lab15_itinerary_agent import run_lab15
from src.module16_complaint_agent.lab16_complaint_agent import run_lab16
from src.module17_multi_agent.lab17_multi_agent import run_lab17
from src.module18_multimodal.lab18_multimodal import run_lab18
from src.module19_safety_grounding.lab19_safety_grounding import run_lab19
from src.module20_final_concierge.lab20_final_agent import run_lab20
from src.module20_final_concierge.final_agent import TheGrandAzureMasterAgent


def run_interactive_chat():
    """Live interactive chat session with Unified Autonomous Concierge Master Agent Julian."""
    print("=" * 80)
    print("🏨 THE GRAND AZURE RESORT & SPA — MASTER CONCIERGE DESK")
    print("   Chief Concierge: Julian Saint-Claire (Les Clefs d'Or)")
    print("   Unified Architecture: RAG • Multi-Agent • Tool Calling • Multimodal • Safety")
    print("   Type 'exit', 'quit', or 'q' to end the conversation.")
    print("   Type 'reset' to start a fresh dialogue session.")
    print("   To analyze an image, prepend: [image: data/sample_images/azure_breeze_menu.jpg]")
    print("=" * 80)

    agent = TheGrandAzureMasterAgent()
    print("\nJulian: \"A warm welcome to The Grand Azure Resort & Spa. It is my absolute honor to assist you. How may I be of service today?\"\n")

    session_id = "cli_live_session"
    room_number = "302"
    guest_name = "Esteemed Guest"

    while True:
        try:
            user_input = input("Guest > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nJulian: Thank you for visiting. Have a pleasant stay!")
            break

        if not user_input:
            continue

        command = user_input.lower()
        if command in ["exit", "quit", "q"]:
            print("\nJulian: Thank you for visiting. Have a pleasant stay!")
            break

        if command == "reset":
            agent = TheGrandAzureMasterAgent()
            print("\n[Concierge desk session reset]\nJulian: How may I begin anew in assisting you, esteemed guest?\n")
            continue

        # Optional image extraction from prompt
        image_input = None
        if "[image:" in user_input.lower():
            img_match = re.search(r'\[image:\s*([^\]]+)\]', user_input, re.IGNORECASE)
            if img_match:
                img_path = img_match.group(1).strip()
                user_input = re.sub(r'\[image:\s*([^\]]+)\]', '', user_input).strip()
                image_input = img_path

        # Process with Master Concierge Agent (Module 20)
        res = agent.process_guest_interaction(
            query=user_input,
            image_input=image_input,
            room_number=room_number,
            guest_name=guest_name,
            session_id=session_id
        )

        print(f"\nJulian:\n\"{res.response_text}\"\n")

        # Telemetry metadata
        print(f"  [⚡ Specialized Agents: {', '.join(res.telemetry.specialized_agents_engaged) or 'concierge'} | "
              f"Grounding: {res.telemetry.grounding_verdict.value} | "
              f"Latency: {res.telemetry.pipeline_duration_ms:.1f}ms]")
        if res.telemetry.tools_called:
            print(f"  [🔧 Tools Executed: {', '.join(res.telemetry.tools_called)}]")
        print("-" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="AI Hotel Concierge Agent - Module Runner")
    parser.add_argument("--module", "-m", type=int, choices=list(range(1, 21)), help="Run a specific module lab (1 to 20)")
    parser.add_argument("--all", "-a", action="store_true", help="Run all 20 modules sequentially")
    parser.add_argument("--chat", "-c", action="store_true", help="Launch interactive live chat with Concierge Julian")

    args = parser.parse_args()

    if args.chat:
        run_interactive_chat()
        return

    module_runners = {
        1: run_lab1,
        2: run_lab2,
        3: run_lab3,
        4: run_lab4,
        5: run_lab5,
        6: run_lab6,
        7: run_lab7,
        8: run_lab8,
        9: run_lab9,
        10: run_lab10,
        11: run_lab11,
        12: run_lab12,
        13: run_lab13,
        14: run_lab14,
        15: run_lab15,
        16: run_lab16,
        17: run_lab17,
        18: run_lab18,
        19: run_lab19,
        20: run_lab20,
    }

    if args.module in module_runners:
        module_runners[args.module]()
    elif args.all or len(sys.argv) == 1:
        print("\n" + "#" * 80)
        print("🚀 EXECUTING ALL 20 MODULES SEQUENTIALLY")
        print("#" * 80 + "\n")
        for mod_num in range(1, 21):
            print(f"\n{'='*30} RUNNING MODULE {mod_num} {'='*30}\n")
            module_runners[mod_num]()
        print("\n" + "#" * 80)
        print("🏆 ALL 20 MODULES COMPLETED SUCCESSFULLY!")
        print("#" * 80)


if __name__ == "__main__":
    main()


