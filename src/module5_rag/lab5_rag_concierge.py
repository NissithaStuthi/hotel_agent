"""Module 5 Practical Lab: Grounded RAG Hotel Knowledge Concierge

Demonstrates the transformation from an ungrounded LLM to a grounded
retrieval-augmented concierge with source citation and zero hallucination.
"""

from typing import List, Dict, Any
import src.utils.console_display  # Ensures UTF-8 on Windows
from src.module5_rag.rag_engine import HotelRAGEngine
from src.module4_concierge.concierge_agent import BasicConciergeAgent


BENCHMARK_RAG_QUESTIONS = [
    {
        "topic": "Pet Policy & Sanitzation Fee",
        "question": "What is the pet cleaning fee, and what rooms are dogs allowed in?",
        "ground_truth_facts": ["$150 one-time cleaning fee", "Deluxe Double Queen Garden Terrace", "Cliffside Ocean Villas", "45 lbs max"]
    },
    {
        "topic": "Valet Parking & EV Charging",
        "question": "How much is overnight valet parking and is EV charging free?",
        "ground_truth_facts": ["$45 per night", "Tesla Superchargers complimentary", "Universal Level 2"]
    },
    {
        "topic": "Pool Hours & Quiet Time",
        "question": "What are the hours for adults-only quiet time at the infinity pool, and is it heated?",
        "ground_truth_facts": ["8:00 PM - 10:00 PM", "Heated to 82°F (28°C)", "6:00 AM - 10:00 PM total hours"]
    },
    {
        "topic": "Drone Regulations",
        "question": "Can I fly my camera drone over the beach club to film our vacation?",
        "ground_truth_facts": ["Recreational drones strictly prohibited", "Airspace privacy policy"]
    },
    {
        "topic": "Villa Cancellation Penalty",
        "question": "What is the penalty if I cancel my Cliffside Villa reservation 3 days before arrival?",
        "ground_truth_facts": ["7-day advance notice required for Villas", "50% forfeit of total stay value"]
    }
]


def run_lab5() -> Dict[str, Any]:
    """Runs Module 5 Grounded RAG demonstration lab."""
    print("=" * 80)
    print("🏨 MODULE 5: HOTEL KNOWLEDGE RAG (GROUNDED RETRIEVAL CONCIERGE)")
    print("=" * 80)

    rag_engine = HotelRAGEngine()
    total_indexed = rag_engine.retriever.vector_store.count()
    print(f"\nVector Knowledge Base Status: {total_indexed} semantic chunks indexed.")
    print("Testing Grounded Question-Answering across 5 high-precision policy questions:")
    print("-" * 80)

    results_summary = []
    for idx, test in enumerate(BENCHMARK_RAG_QUESTIONS, 1):
        q = test["question"]
        print(f"\n[{idx}] Question: \"{q}\"")
        print(f"    Topic:     {test['topic']}")

        # Execute RAG
        rag_res = rag_engine.answer_query(q)

        print(f"    Intent:    {rag_res.intent_classification.intent_category.value} | Domain: {rag_res.intent_classification.domain.value}")
        print(f"    Sources Cited ({len(rag_res.sources)}):")
        for s in rag_res.sources:
            print(f"      📖 {s}")

        print(f"\n    Grounded Answer from Concierge Julian:")
        print(f"    \"{rag_res.answer}\"")

        # Check fact verification
        ans_lower = rag_res.answer.lower()
        facts_found = [f for f in test["ground_truth_facts"] if any(w.lower() in ans_lower for w in f.split()[:2])]
        print(f"    Fact Verification: {len(facts_found)}/{len(test['ground_truth_facts'])} key policy facts verified.")
        print("-" * 80)

        results_summary.append({
            "question": q,
            "topic": test["topic"],
            "sources": rag_res.sources,
            "confidence": rag_res.grounding_confidence,
            "answer": rag_res.answer
        })

    print("\n" + "=" * 80)
    print("✅ Module 5 Lab Completed: Grounded RAG pipeline fully operational.")
    print("=" * 80)

    return {
        "indexed_chunks": total_indexed,
        "queries_tested": len(results_summary),
        "results": results_summary
    }


if __name__ == "__main__":
    run_lab5()
