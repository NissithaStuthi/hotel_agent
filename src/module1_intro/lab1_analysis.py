"""Module 1 Practical Lab: Request Categorization & Architectural Analysis

Executes hands-on analysis of hotel guest requests, categorization patterns,
and architectural comparisons between Chatbots, GenAI, and Agentic AI.
"""

from collections import Counter
from typing import Dict, List, Any
import src.utils.console_display  # Ensures UTF-8 on Windows
from src.module1_intro.taxonomy import (
    SCENARIO_CATALOG,
    ARCHITECTURAL_COMPARISON,
    RequestCategory,
    RequestDomain,
    UrgencyLevel
)


def run_lab1() -> Dict[str, Any]:
    """Runs Module 1 practical lab and returns analytical metrics."""
    print("=" * 80)
    print("🏨 MODULE 1: INTRODUCTION TO AI HOTEL CONCIERGE & REQUEST TAXONOMY")
    print("=" * 80)

    # 1. Architectural Comparison Summary
    print("\n[PART 1] Architectural Evolution in Hospitality AI:")
    print("-" * 80)
    for model_name, details in ARCHITECTURAL_COMPARISON.items():
        print(f"\n🔹 {model_name.upper()}")
        print(f"   Hospitality Fit: {details['Hospitality Fit']}")
        print("   Key Capabilities:")
        for cap in details['Capabilities'][:2]:
            print(f"     • {cap}")
        print("   Limitations:")
        for lim in details['Limitations'][:2]:
            print(f"     • {lim}")

    # 2. Scenario Catalog Breakdown
    total_scenarios = len(SCENARIO_CATALOG)
    categories = [s.category.value for s in SCENARIO_CATALOG]
    domains = [s.domain.value for s in SCENARIO_CATALOG]
    urgencies = [s.urgency.value for s in SCENARIO_CATALOG]

    category_counts = Counter(categories)
    domain_counts = Counter(domains)
    urgency_counts = Counter(urgencies)

    print("\n" + "=" * 80)
    print(f"[PART 2] Analysis of {total_scenarios} Real-World Hotel Guest Scenarios:")
    print("-" * 80)

    print("\n📊 Breakdown by Primary Request Category:")
    for cat, count in category_counts.most_common():
        pct = (count / total_scenarios) * 100
        bar = "█" * int(pct / 4)
        print(f"  {cat:<24} : {count:>2} ({pct:>5.1f}%) | {bar}")

    print("\n🏢 Breakdown by Operational Domain:")
    for dom, count in domain_counts.most_common():
        pct = (count / total_scenarios) * 100
        print(f"  {dom:<32} : {count:>2} ({pct:>5.1f}%)")

    print("\n⏱️ Breakdown by Urgency Level:")
    for urg, count in urgency_counts.most_common():
        pct = (count / total_scenarios) * 100
        print(f"  {urg:<12} : {count:>2} ({pct:>5.1f}%)")

    # 3. Detailed Scenario Walkthrough
    print("\n" + "=" * 80)
    print("[PART 3] Representative Scenarios & Routing Actions:")
    print("-" * 80)
    for scenario in SCENARIO_CATALOG[:6]:
        print(f"\n[{scenario.id}] Category: {scenario.category.value} | Domain: {scenario.domain.value} | Urgency: {scenario.urgency.value}")
        print(f"   Guest Query:     \"{scenario.guest_query}\"")
        print(f"   Guest Context:   {scenario.guest_context}")
        print(f"   Action Required: {scenario.expected_action}")
        print(f"   Target System:   {scenario.suitable_architecture}")

    print("\n" + "=" * 80)
    print("✅ Module 1 Lab Completed: Taxonomy defined and guest request patterns verified.")
    print("=" * 80)

    return {
        "total_scenarios": total_scenarios,
        "category_counts": dict(category_counts),
        "domain_counts": dict(domain_counts),
        "urgency_counts": dict(urgency_counts)
    }


if __name__ == "__main__":
    run_lab1()
