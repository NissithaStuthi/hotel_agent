"""Module 18: Multimodal Concierge - Models

Defines structured schemas for image category classification, visual feature extraction,
multimodal query inputs, and grounded visual responses.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ImageCategory(str, Enum):
    MENU_PHOTO = "menu_photo"
    HOTEL_MAP = "hotel_map"
    FOOD_DISH = "food_dish"
    TOURIST_ATTRACTION = "tourist_attraction"
    ROOM_AMENITY = "room_amenity"
    MAINTENANCE_DEFECT = "maintenance_defect"
    GENERAL = "general"


class VisualEntity(BaseModel):
    name: str
    category: str
    confidence: float = 0.95
    attributes: Dict[str, Any] = Field(default_factory=dict)


class VisualAnalysisResult(BaseModel):
    category: ImageCategory
    scene_description: str
    extracted_text_or_tags: List[str] = Field(default_factory=list)
    recognized_entities: List[VisualEntity] = Field(default_factory=list)
    confidence: float = 0.92
    source_model: str = "Local-VLM-Hybrid"


class MultimodalResponse(BaseModel):
    question: str
    image_name: str
    visual_analysis: VisualAnalysisResult
    retrieved_knowledge: List[str] = Field(default_factory=list)
    concierge_answer: str
    grounding_confidence: float = 0.95
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
