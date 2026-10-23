"""Module 18: Multimodal Concierge - Lab Runner

Demonstrates image understanding and visual question answering for:
1. Food dishes ("What is this dish?")
2. Hotel maps ("Which facility is shown on this hotel map?")
3. Restaurant menus ("Are there gluten-free dishes on this menu?")
4. Local tourist attractions ("What is this location?")
5. In-room appliances / thermostat photos ("What does this thermostat reading mean?")
"""

from pathlib import Path
import src.utils.console_display  # Windows UTF-8 support
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.config import DATA_DIR
from src.module18_multimodal.multimodal_concierge import MultimodalConcierge


def run_lab18():
    console = Console()
    console.print(Panel.fit(
        "[bold cyan]🖼️ MODULE 18: MULTIMODAL CONCIERGE[/bold cyan]\n"
        "[dim]Vision-Language Understanding • Image Classification • Knowledge Grounding • Clefs d'Or Response[/dim]",
        border_style="cyan"
    ))

    # Pipeline Diagram
    pipeline_diag = """
    [bold yellow]Image + Question[/bold yellow] (Uploaded Menu, Map, Dish, Attraction, Thermostat)
           ↓
    [cyan]Vision-Language Model / Feature Extractor[/cyan]
           ↓
    [magenta]Visual Understanding & Entity Extraction[/magenta]
           ↓
    [blue]Hotel Knowledge Retrieval (RAG Vector Store)[/blue]
           ↓
    [green]Grounded Luxury Synthesis Engine[/green]
           ↓
    [bold gold1]Comprehensive Grounded Answer[/bold gold1]
    """
    console.print(Panel(pipeline_diag, title="Multimodal Understanding Pipeline", border_style="bright_blue"))

    concierge = MultimodalConcierge()
    sample_dir = DATA_DIR / "sample_images"

    test_cases = [
        ("signature_sea_bass.jpg", "What is this dish, and which restaurant serves it?", "Countess Maria", "Dish Visual Understanding"),
        ("hotel_resort_map.jpg", "Which facility is shown on this hotel map and where is the pool located?", "Lord Sterling", "Resort Map Navigation"),
        ("azure_breeze_menu.jpg", "Are there gluten-free or dairy-free options on this menu?", "Dr. Aris", "Menu Analysis"),
        ("emerald_cove_sea_caves.jpg", "What attraction is this and what is the best time to visit?", "Elena Rostova", "Tourist Attraction Identification"),
        ("in_room_thermostat.jpg", "The thermostat shows 68°F, is the cooling working properly?", "Suite 302", "In-Room Appliance Diagnosis"),
    ]

    summary_table = Table(title="Multimodal Concierge Visual Inquiries", border_style="cyan")
    summary_table.add_column("Image File", style="bold white", width=22)
    summary_table.add_column("Detected Category", style="yellow")
    summary_table.add_column("Key Recognized Entity", style="cyan", width=30)
    summary_table.add_column("Grounding Confidence", style="bold green", justify="center")

    for idx, (img_filename, question, guest, label) in enumerate(test_cases, start=1):
        img_path = sample_dir / img_filename
        if not img_path.exists():
            console.print(f"[red]Missing test image: {img_path}[/red]")
            continue

        console.print(f"\n[bold yellow]── [Test Case {idx}] {label} ──[/bold yellow]")
        console.print(f"[bold]Image Asset:[/bold] `{img_filename}` | [bold]Guest Question:[/bold] \"{question}\"")

        res = concierge.process_multimodal_query(img_path, question=question, guest_name=guest)
        primary_entity = res.visual_analysis.recognized_entities[0].name if res.visual_analysis.recognized_entities else "N/A"

        summary_table.add_row(
            img_filename,
            res.visual_analysis.category.value,
            primary_entity[:30],
            f"{res.grounding_confidence * 100:.1f}%",
        )

        console.print(f"[bold cyan]Visual Analysis:[/bold cyan] {res.visual_analysis.scene_description}")
        console.print(f"[bold]Extracted Visual Tags:[/bold] {', '.join(res.visual_analysis.extracted_text_or_tags)}")
        console.print(Panel(res.concierge_answer, title=f"Chief Concierge Julian Saint-Claire (to {guest})", border_style="bright_blue"))

    console.print("\n")
    console.print(summary_table)
    console.print("[bold green]✔ Module 18 Multimodal Concierge successfully verified![/bold green]\n")


if __name__ == "__main__":
    run_lab18()
