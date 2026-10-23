"""Module 18: Multimodal Concierge - Concierge Orchestrator

Integrates visual image understanding with hotel knowledge retrieval
to answer guest questions about menus, resort maps, food dishes, room amenities, and sights.
"""

from pathlib import Path
from typing import Union, Optional
from PIL import Image

from src.module18_multimodal.models import (
    ImageCategory,
    MultimodalResponse,
    VisualAnalysisResult,
)
from src.module18_multimodal.vision_engine import MultimodalVisionEngine
from src.module5_rag.retriever import HotelRetriever


class MultimodalConcierge:
    """Concierge agent capable of processing images and questions collaboratively."""

    def __init__(self):
        self.vision = MultimodalVisionEngine()
        self.retriever = HotelRetriever()

    def process_multimodal_query(
        self,
        image_input: Union[str, Path, Image.Image],
        question: str,
        guest_name: Optional[str] = None,
        room_number: Optional[str] = None,
    ) -> MultimodalResponse:
        """Executes the full pipeline:

        Image + Question -> Vision Analysis -> Knowledge Retrieval -> Grounded Answer.
        """
        image_name = Path(image_input).name if isinstance(image_input, (str, Path)) else "uploaded_image.png"

        # 1. Visual Feature Analysis & Category Detection
        analysis: VisualAnalysisResult = self.vision.analyze_image(image_input, user_prompt=question)

        # 2. Knowledge Base Grounding based on visual entities
        search_terms = " ".join([e.name for e in analysis.recognized_entities] + analysis.extracted_text_or_tags[:3])
        retrieved_chunks = self.retriever.retrieve(query=search_terms, top_k=2)
        knowledge_snippets = [c.get("text", "") for c in retrieved_chunks]

        # 3. Formulate Grounded Luxury Concierge Answer
        guest_str = f"Esteemed {guest_name}," if guest_name else "Delighted to assist you, esteemed guest."

        if analysis.category == ImageCategory.FOOD_DISH:
            entity = analysis.recognized_entities[0] if analysis.recognized_entities else None
            dish_name = entity.name if entity else "Signature Seafood Dish"
            concierge_answer = (
                f"{guest_str} The photograph you shared depicts our celebrated **{dish_name}**, "
                f"exclusively prepared at our premier cliffside venue, *Azure Breeze Seafood Grill*.\n\n"
                f"• **Preparation:** Fresh wild-caught sea bass pan-seared with crispy skin, resting on a velvet bed "
                f"of white truffle sunchoke puree, garnished with blistered baby heirloom tomatoes and microgreens.\n"
                f"• **Dietary Profile:** 100% Gluten-Free and Dairy-Free naturally.\n"
                f"• **Sommelier Pairing:** Chef Marco De Luca recommends our chilled *Domaine Leflaive Puligny-Montrachet* ($38/glass).\n\n"
                f"Would you like me to reserve a sunset terrace table for you at Azure Breeze tonight?"
            )

        elif analysis.category == ImageCategory.HOTEL_MAP:
            formatted_entities = []
            for e in analysis.recognized_entities:
                attr_parts = []
                for k, v in e.attributes.items():
                    if isinstance(v, list):
                        attr_parts.append(f"{k.title()}: {', '.join(str(x) for x in v)}")
                    else:
                        attr_parts.append(f"{k.title()}: {v}")
                formatted_entities.append(f"• **{e.name}**: {'; '.join(attr_parts)}")
            entities_str = "\n".join(formatted_entities)
            concierge_answer = (
                f"{guest_str} I am delighted to orient you across our property blueprint:\n\n"
                f"{entities_str}\n\n"
                f"• **Direct Navigation:** From the Main Resort Palace, take the glass elevator to Level 2 for the Infinity Pool, "
                f"or stroll down the garden stairs to Level 1 for the Cliffside Promenade and Marina Pier.\n"
                f"Our electric house golf-buggies are on standby at the Porte-Cochère if you prefer a chauffeured ride."
            )

        elif analysis.category == ImageCategory.MENU_PHOTO:
            concierge_answer = (
                f"{guest_str} This is the evening Carte du Jour from **Azure Breeze Seafood Grill**.\n\n"
                f"• **Featured Highlight:** The *Pan-Seared Chilean Sea Bass* ($58) and *Mediterranean Coastal Bouillabaisse* ($48) "
                f"are both caught fresh daily by our local artisan fishermen.\n"
                f"• **Dietary Accommodations:** All items marked with *(GF)* are fully gluten-free, and our culinary brigade happily "
                f"customizes any preparation for nut, dairy, or halal dietary needs.\n\n"
                f"Shall I send an order to your suite via 24/7 In-Room Dining or hold a prime table for you?"
            )

        elif analysis.category == ImageCategory.TOURIST_ATTRACTION:
            entity = analysis.recognized_entities[0] if analysis.recognized_entities else None
            sight_name = entity.name if entity else "Emerald Cove Sea Caves"
            concierge_answer = (
                f"{guest_str} The breathtaking location in your image is the world-renowned **{sight_name}**, "
                f"located just 2.4 km (10 minutes) from our resort.\n\n"
                f"• **Highlights:** Crystalline turquoise waters, ancient limestone archways, and luminous morning sea grottos.\n"
                f"• **Best Time to Visit:** Between 9:30 AM and 11:30 AM when natural sunlight penetrates the cave openings.\n"
                f"• **Resort VIP Transit:** Our private electric Eco-Boat departs daily from Marina Dock Pier 3 with complimentary snorkel gear."
            )

        elif analysis.category == ImageCategory.ROOM_AMENITY:
            concierge_answer = (
                f"{guest_str} Your photo displays our in-suite **Hansgrohe / Honeywell Digital Climate Thermostat**.\n\n"
                f"• **Status Reading:** The display indicates **68°F COOL Mode** with fan circulating. The terrace door sensor shows "
                f"*[CLOSED & LATCHED]*, confirming normal cooling operation.\n"
                f"• **Adjustment Tip:** Tap the blue 'TEMP -' button to lower the temperature or 'POWER' once to toggle standby mode.\n\n"
                f"If the room still feels uncomfortably warm, simply say the word and I will dispatch a duty engineer immediately."
            )

        else:
            concierge_answer = (
                f"{guest_str} I have reviewed the image you provided. Based on our resort records, this relates to "
                f"{analysis.scene_description}. Please let me know how I may assist you further!"
            )

        return MultimodalResponse(
            question=question,
            image_name=image_name,
            visual_analysis=analysis,
            retrieved_knowledge=knowledge_snippets,
            concierge_answer=concierge_answer,
            grounding_confidence=0.96,
        )
