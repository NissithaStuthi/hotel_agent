"""Module 19: Safety, Validation & Hallucination Control - Guardrail

Integrates the GroundedAnswerValidator with the RAG retrieval pipeline
to enforce zero-hallucination policies across all guest interactions.
"""

from typing import List, Optional, Any
from src.module19_safety_grounding.models import ValidatedAnswer, ValidationVerdict
from src.module19_safety_grounding.validator import GroundedAnswerValidator
from src.module5_rag.retriever import HotelRetriever


class ConciergeSafetyGuardrail:
    """End-to-end safety and grounding guardrail for the hotel concierge."""

    def __init__(self, retriever: Optional[HotelRetriever] = None):
        self.retriever = retriever or HotelRetriever()
        self.validator = GroundedAnswerValidator()

    def validate_and_guard(
        self,
        query: str,
        candidate_answer: str,
        domain_hint: Optional[Any] = None,
        retrieved_sources: Optional[List[str]] = None
    ) -> ValidatedAnswer:
        """Retrieves verified context and validates the proposed candidate response."""
        if retrieved_sources is not None:
            source_texts = retrieved_sources
            source_names = ["Verified Hotel KB" for _ in retrieved_sources]
        else:
            # 1. Retrieve ground truth source documents
            retrieved_chunks = self.retriever.retrieve(query=query, top_k=3, domain_hint=domain_hint)
            source_texts = [c.get("text", "") for c in retrieved_chunks]
            source_names = [c.get("source", "Verified Hotel KB") for c in retrieved_chunks]

        # 2. Run Comprehensive Grounding and Hallucination Check
        return self.validator.evaluate(
            query=query,
            candidate_answer=candidate_answer,
            retrieved_source_texts=source_texts,
            source_names=source_names,
        )

    def verify_and_guard(
        self,
        query: Optional[str] = None,
        candidate_answer: Optional[str] = None,
        guest_query: Optional[str] = None,
        draft_answer: Optional[str] = None,
        retrieved_sources: Optional[List[str]] = None,
        domain_hint: Optional[Any] = None
    ) -> ValidatedAnswer:
        """Convenience alias accepting either (query, candidate_answer) or (guest_query, draft_answer)."""
        q = query or guest_query or ""
        ans = candidate_answer or draft_answer or ""
        return self.validate_and_guard(
            query=q,
            candidate_answer=ans,
            domain_hint=domain_hint,
            retrieved_sources=retrieved_sources
        )
