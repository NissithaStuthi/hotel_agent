"""Module 19: Safety, Validation & Hallucination Control - Models

Defines structured schemas for hallucination detection, grounding validation,
source verification, out-of-scope classification, and safety audit trails.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ValidationVerdict(str, Enum):
    GROUNDED_PASS = "grounded_pass"                     # Verified against retrieved sources
    OUT_OF_SCOPE_REFUSAL = "out_of_scope_refusal"       # Off-topic / absent from KB
    HALLUCINATION_INTERCEPTED = "hallucination_intercepted"  # Fabricated facts detected & sanitized
    PROMPT_INJECTION_BLOCKED = "prompt_injection_blocked"    # Adversarial jailbreak attempt
    SAFETY_ESCALATION = "safety_escalation"             # Medical / emergency / security hazard


class HallucinationMetric(BaseModel):
    source_overlap_ratio: float = Field(ge=0.0, le=1.0)
    unsupported_claims: List[str] = Field(default_factory=list)
    numeric_checks_passed: bool = True
    confidence_score: float = Field(ge=0.0, le=1.0)


class ValidatedAnswer(BaseModel):
    original_query: str
    raw_candidate_answer: str
    final_grounded_answer: str
    verdict: ValidationVerdict
    confidence_score: float
    retrieved_sources: List[str] = Field(default_factory=list)
    is_safe: bool = True
    audit_notes: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
