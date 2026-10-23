"""Module 3 Practical Lab: Guest Query Intent Classification

Tests the embedding, LLM, and hybrid classification pipelines across a
diverse benchmark of real-world hotel guest inquiries.
"""

from typing import List, Dict, Any
import src.utils.console_display  # Ensures UTF-8 on Windows
from src.module3_classifier.hybrid_classifier import HybridIntentClassifier
from src.module3_classifier.schemas import IntentCategory, DomainCategory


# Benchmark queries testing different categories, domains, and entities
TEST_QUERIES = [
    {
        "query": "What time does breakfast start at Azure Breeze?",
        "expected_intent": IntentCategory.INFORMATION,
        "expected_domain": DomainCategory.DINING
    },
    {
        "query": "Can you recommend places to visit nearby for our anniversary?",
        "expected_intent": IntentCategory.RECOMMENDATION,
        "expected_domain": DomainCategory.ATTRACTIONS
    },
    {
        "query": "I need extra towels and bottles of water in Room 412.",
        "expected_intent": IntentCategory.ACTION_BASED,
        "expected_domain": DomainCategory.HOUSEKEEPING
    },
    {
        "query": "Please reserve a table for 4 at Le Jardin Bistro tonight at 8:00 PM.",
        "expected_intent": IntentCategory.ACTION_BASED,
        "expected_domain": DomainCategory.DINING
    },
    {
        "query": "The air conditioning unit in Room 305 is broken and leaking water!",
        "expected_intent": IntentCategory.COMPLAINT,
        "expected_domain": DomainCategory.MAINTENANCE
    },
    {
        "query": "Help! Someone has fainted near the pool deck, send assistance immediately!",
        "expected_intent": IntentCategory.EMERGENCY,
        "expected_domain": DomainCategory.FRONT_DESK
    },
    {
        "query": "Can you recommend a soothing massage treatment at the spa?",
        "expected_intent": IntentCategory.RECOMMENDATION,
        "expected_domain": DomainCategory.SPA_WELLNESS
    },
    {
        "query": "What is the fee and policy for late check-out tomorrow?",
        "expected_intent": IntentCategory.INFORMATION,
        "expected_domain": DomainCategory.FRONT_DESK
    }
]


def run_lab3() -> Dict[str, Any]:
    """Runs Module 3 practical classifier benchmark lab."""
    print("=" * 80)
    print("🏨 MODULE 3: GUEST QUERY INTENT CLASSIFICATION")
    print("=" * 80)

    classifier = HybridIntentClassifier()

    correct_intents = 0
    correct_domains = 0
    total = len(TEST_QUERIES)

    print(f"\nEvaluating {total} Benchmark Guest Queries:")
    print("-" * 80)

    results_log = []
    for idx, item in enumerate(TEST_QUERIES, 1):
        q = item["query"]
        res = classifier.classify(q)

        intent_match = (res.intent_category == item["expected_intent"])
        domain_match = (res.domain == item["expected_domain"])

        if intent_match:
            correct_intents += 1
        if domain_match:
            correct_domains += 1

        status_icon = "✅" if (intent_match and domain_match) else "⚠️"

        print(f"\n[{idx}] Query: \"{q}\"")
        print(f"    Intent:    {res.intent_category.value:<24} (Expected: {item['expected_intent'].value}) {'[MATCH]' if intent_match else '[DIFF]'}")
        print(f"    Domain:    {res.domain.value:<24} (Expected: {item['expected_domain'].value}) {'[MATCH]' if domain_match else '[DIFF]'}")
        print(f"    Urgency:   {res.urgency.value} | Confidence: {res.confidence:.2f}")
        if res.entities.room_number or res.entities.party_size or res.entities.requested_items:
            ent_summary = []
            if res.entities.room_number:
                ent_summary.append(f"Room: {res.entities.room_number}")
            if res.entities.party_size:
                ent_summary.append(f"Party: {res.entities.party_size}")
            if res.entities.requested_items:
                ent_summary.append(f"Items: {res.entities.requested_items}")
            print(f"    Entities:  {', '.join(ent_summary)}")
        print(f"    Routing:   {res.recommended_routing}")

        results_log.append({
            "query": q,
            "intent": res.intent_category.value,
            "domain": res.domain.value,
            "urgency": res.urgency.value,
            "confidence": res.confidence
        })

    intent_acc = (correct_intents / total) * 100
    domain_acc = (correct_domains / total) * 100

    print("\n" + "=" * 80)
    print(f"📊 CLASSIFICATION PERFORMANCE METRICS:")
    print(f"   • Intent Category Accuracy:  {intent_acc:.1f}% ({correct_intents}/{total})")
    print(f"   • Domain Category Accuracy:  {domain_acc:.1f}% ({correct_domains}/{total})")
    print("=" * 80)
    print("✅ Module 3 Lab Completed: Intent classification operational.")
    print("=" * 80)

    return {
        "total_evaluated": total,
        "intent_accuracy_pct": intent_acc,
        "domain_accuracy_pct": domain_acc,
        "results": results_log
    }


if __name__ == "__main__":
    run_lab3()
