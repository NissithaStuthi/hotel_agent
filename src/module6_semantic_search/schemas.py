"""Module 6: Semantic Hotel Search - Data Schemas"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SearchDomain(str, Enum):
    """Domains for semantic search filtering."""
    ALL = "all"
    SPA = "spa"
    LOUNGE = "lounge"
    POOL = "pool"
    GARDEN = "garden"
    DINING = "dining"
    ROOMS = "rooms"
    AMENITIES = "amenities"
    POLICIES = "policies"
    ATTRACTIONS = "attractions"
    TRANSPORTATION = "transportation"


class SearchResult(BaseModel):
    """Single search result with metadata."""
    content: str
    source: str
    domain: SearchDomain
    score: float = Field(ge=0.0, le=1.0)
    chunk_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SemanticSearchQuery(BaseModel):
    """Query for semantic search."""
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    domains: List[SearchDomain] = Field(default_factory=lambda: [SearchDomain.ALL])
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)
    include_metadata: bool = True


class SemanticSearchResponse(BaseModel):
    """Response from semantic search."""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    embedding_model: str


class RelaxationSearchRequest(BaseModel):
    """Specialized request for relaxation-related queries."""
    query: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
    time_of_day: Optional[str] = None
    party_size: Optional[int] = None
    top_k: int = 5


class RelaxationOption(BaseModel):
    """A relaxation option with details."""
    name: str
    type: str
    description: str
    location: str
    hours: str
    amenities: List[str] = Field(default_factory=list)
    suitability_score: float = Field(ge=0.0, le=1.0)
    source: str


class RelaxationSearchResponse(BaseModel):
    """Response for relaxation search."""
    query: str
    options: List[RelaxationOption]
    reasoning: str