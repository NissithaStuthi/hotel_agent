"""Module 9: Personalized Recommendations — Lab Execution

Demonstrates:
1. Extracting guest preferences & travel party constraints from queries
2. Recommendation engine using embeddings + multi-criteria constraint scoring:
   - Family-friendly attractions
   - Proximity & distance (km)
   - Opening hours & schedules
   - Guest preferences
3. LLM reasoning layer explaining the rationale behind recommendations
4. Comparison of family scenario vs. couples scenario
"""

import sys
import src.utils.console_display  # Windows UTF-8 console support
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.module9_recommendations.recommendation_engine import PersonalizedRecommendationEngine
from src.module9_recommendations.models import GuestProfile


def run_lab9():
    console = Console()
    console.print(Panel.fit(
        "[bold gold1]MODULE 9: PERSONALIZED RECOMMENDATIONS[/bold gold1]\n"
        "[italic cyan]Multi-Criteria Engine: Embeddings + Preferences + Distance + Hours + LLM Reasoning[/italic cyan]",
        border_style="gold1"
    ))

    engine = PersonalizedRecommendationEngine()

    # 1. Primary Scenario from Course Prompt: "I am traveling with children. What can we do nearby?"
    query_family = "I am traveling with children. What can we do nearby?"
    console.print(f"\n[bold cyan]1. Executing Primary Scenario:[/bold cyan] [italic yellow]\"{query_family}\"[/italic yellow]\n")

    response_fam = engine.recommend(query=query_family, top_n=4)

    profile_fam = response_fam.guest_profile
    console.print(f"[bold white]Detected Profile Constraints:[/bold white] Party=[bold green]{profile_fam.party_type}[/bold green] | Max Distance=[bold green]{profile_fam.max_distance_km} km[/bold green] | Interests=[bold green]{', '.join(profile_fam.interests)}[/bold green]\n")

    # Table of Scored Recommendations
    rec_table = Table(title="Multi-Criteria Ranked Recommendations (Family with Children)", header_style="bold gold1")
    rec_table.add_column("Rank", justify="center", style="dim")
    rec_table.add_column("Candidate Activity", style="bold cyan")
    rec_table.add_column("Distance", justify="center", style="green")
    rec_table.add_column("Hours", justify="center", style="blue")
    rec_table.add_column("Family", justify="center", style="yellow")
    rec_table.add_column("Dist Score", justify="center", style="magenta")
    rec_table.add_column("Composite", justify="center", style="bold green")

    for idx, rec in enumerate(response_fam.recommendations, 1):
        c = rec.candidate
        dist_str = f"{c.distance_km} km (On-site)" if c.distance_km == 0.0 else f"{c.distance_km} km"
        rec_table.add_row(
            str(idx),
            c.name,
            dist_str,
            c.operating_hours,
            f"{rec.family_alignment_score:.2f}",
            f"{rec.distance_score:.2f}",
            f"{rec.composite_score:.2f}"
        )

    console.print(rec_table)

    # Detailed Reasoning Breakdown
    console.print("\n[bold cyan]Personalization & Safety Reasoning Breakdown:[/bold cyan]")
    for idx, rec in enumerate(response_fam.recommendations, 1):
        console.print(f"[bold yellow]#{idx} {rec.candidate.name}:[/bold yellow] {rec.personalization_reasoning}")

    # Concierge Advice Output
    console.print("\n[bold cyan]Concierge Julian's Personalized Advice:[/bold cyan]")
    console.print(Panel(response_fam.concierge_advice, title="Personalized Response", border_style="gold1"))

    # 2. Comparison Scenario: Romantic Couple
    console.print("\n" + "=" * 75)
    query_couple = "We are celebrating our 10th wedding anniversary, looking for an intimate romantic evening."
    console.print(f"\n[bold cyan]2. Comparison Scenario (Couples vs. Family):[/bold cyan] [italic yellow]\"{query_couple}\"[/italic yellow]\n")

    response_cpl = engine.recommend(query=query_couple, top_n=3)

    cpl_table = Table(title="Ranked Recommendations (Romantic Couple Profile)", header_style="bold magenta")
    cpl_table.add_column("Rank", justify="center", style="dim")
    cpl_table.add_column("Candidate Activity", style="bold cyan")
    cpl_table.add_column("Distance", justify="center")
    cpl_table.add_column("Category", style="green")
    cpl_table.add_column("Composite", justify="center", style="bold green")

    for idx, rec in enumerate(response_cpl.recommendations, 1):
        cpl_table.add_row(
            str(idx),
            rec.candidate.name,
            f"{rec.candidate.distance_km} km",
            rec.candidate.category,
            f"{rec.composite_score:.2f}"
        )

    console.print(cpl_table)
    console.print(f"[dim]Top Romantic Pick: {response_cpl.recommendations[0].candidate.name} (Adults Only, Oceanfront Suite)[/dim]")

    console.print("\n[bold green][OK] Module 9 Lab Completed Successfully![/bold green]\n")


if __name__ == "__main__":
    run_lab9()
