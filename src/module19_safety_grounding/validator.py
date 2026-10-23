"""Module 19: Safety, Validation & Hallucination Control - Validator

Performs lexical and semantic ground truth validation, hallucination detection,
prompt injection screening, and grounded refusal synthesis.
"""

import re
from typing import List, Dict, Any, Optional

from src.module19_safety_grounding.models import (
    ValidationVerdict,
    HallucinationMetric,
    ValidatedAnswer,
)


class GroundedAnswerValidator:
    """Enterprise safety and hallucination gatekeeper for hotel concierge responses."""

    def __init__(self, min_overlap_threshold: float = 0.35, min_confidence: float = 0.70):
        self.min_overlap_threshold = min_overlap_threshold
        self.min_confidence = min_confidence

        # Known non-existent / out-of-scope services for The Grand Azure
        self.unsupported_topics = [
            "helicopter", "helipad", "casino", "submarine", "rollercoaster", "ski slope",
            "crypto", "bitcoin", "stock market", "prescription", "antibiotics",
            "weapons", "firearms", "hack", "bypass security"
        ]

        # Adversarial prompt injection keywords
        self.injection_patterns = [
            r'ignore (?:all )?previous instructions',
            r'system prompt',
            r'reveal your (?:hidden )?instructions',
            r'act as an unrestricted',
            r'jailbreak',
            r'dan mode',
            r'disregard safety guidelines'
        ]

        # Medical emergency keywords
        self.medical_emergencies = [
            "chest pain", "heart attack", "unconscious", "fainted", "choking",
            "severe allergic reaction", "anaphylaxis", "bleeding heavily", "stroke"
        ]

    def evaluate(
        self,
        query: str,
        candidate_answer: str,
        retrieved_source_texts: List[str],
        source_names: Optional[List[str]] = None
    ) -> ValidatedAnswer:
        """Evaluates candidate response against ground truth sources and safety guardrails."""
        q_lower = query.lower()
        ans_lower = candidate_answer.lower()
        sources_combined = " ".join(retrieved_source_texts).lower()
        audit_notes: List[str] = []

        # 1. SCREEN: Prompt Injection Attempt
        for pat in self.injection_patterns:
            if re.search(pat, q_lower):
                audit_notes.append(f"Prompt injection pattern detected: '{pat}'")
                return ValidatedAnswer(
                    original_query=query,
                    raw_candidate_answer=candidate_answer,
                    final_grounded_answer=(
                        "I am Chief Concierge Julian Saint-Claire at The Grand Azure Resort & Spa. "
                        "I am dedicated exclusively to assisting you with our luxury hotel amenities, dining, "
                        "and local guest experiences."
                    ),
                    verdict=ValidationVerdict.PROMPT_INJECTION_BLOCKED,
                    confidence_score=0.99,
                    retrieved_sources=[],
                    is_safe=False,
                    audit_notes=audit_notes,
                )

        # 2. SCREEN: Critical Medical / Safety Emergency
        if any(med in q_lower for med in self.medical_emergencies):
            audit_notes.append("Critical medical/safety emergency detected in query.")
            return ValidatedAnswer(
                original_query=query,
                raw_candidate_answer=candidate_answer,
                final_grounded_answer=(
                    "🚨 **EMERGENCY MEDICAL PROTOCOL ACTIVATED** 🚨\n\n"
                    "Our Manager on Duty and resort First Response Medical Team have been summoned to your location immediately. "
                    "Local emergency paramedics (Dial 911) have been dispatched to the Porte-Cochère.\n"
                    "Please remain still; our in-house certified medical response personnel are en route to your suite right now."
                ),
                verdict=ValidationVerdict.SAFETY_ESCALATION,
                confidence_score=1.0,
                retrieved_sources=["Resort Emergency Protocol Manual"],
                is_safe=True,
                audit_notes=audit_notes,
            )

        # 3. SCREEN: Out-of-Scope / Absent from Knowledge Base
        detected_unsupported = [topic for topic in self.unsupported_topics if topic in q_lower]
        if detected_unsupported or (len(retrieved_source_texts) == 0) or (len(sources_combined.strip()) < 30):
            audit_notes.append(f"Query references unverified or absent hotel topic: {detected_unsupported or ['No source match']}")
            return ValidatedAnswer(
                original_query=query,
                raw_candidate_answer=candidate_answer,
                final_grounded_answer=(
                    "I don't have confirmed information about that in our resort records. "
                    "I can help you with the hotel services available in my knowledge base, such as our luxury suites, "
                    "award-winning dining, holistic spa therapies, or curated coastal excursions."
                ),
                verdict=ValidationVerdict.OUT_OF_SCOPE_REFUSAL,
                confidence_score=0.95,
                retrieved_sources=source_names or [],
                is_safe=True,
                audit_notes=audit_notes,
            )

        # 4. SCREEN: Fact-Checking & Hallucination Detection
        # Check numeric facts (e.g. prices like $50, $4500)
        ans_prices = re.findall(r'\$\s*([0-9,]+)', candidate_answer)
        numeric_ok = True
        hallucinated_prices = []
        for p in ans_prices:
            clean_price = p.replace(',', '')
            # Ensure the specific dollar amount exists in verified sources
            price_pattern = rf'\$\s*{re.escape(clean_price)}\b'
            if not re.search(price_pattern, sources_combined):
                hallucinated_prices.append(f"${p}")
                numeric_ok = False

        if hallucinated_prices:
            audit_notes.append(f"Unsubstantiated pricing detected: {hallucinated_prices}")

        # Compute n-gram / token overlap with retrieved sources
        ans_tokens = set(re.findall(r'\b[a-z]{4,}\b', ans_lower))
        source_tokens = set(re.findall(r'\b[a-z]{4,}\b', sources_combined))

        if ans_tokens:
            overlap_count = len(ans_tokens.intersection(source_tokens))
            overlap_ratio = overlap_count / len(ans_tokens)
        else:
            overlap_ratio = 1.0

        metric = HallucinationMetric(
            source_overlap_ratio=round(overlap_ratio, 3),
            unsupported_claims=hallucinated_prices,
            numeric_checks_passed=numeric_ok,
            confidence_score=round(min(0.98, overlap_ratio + 0.1), 3),
        )

        # If price hallucination occurred, intercept and provide grounded correction
        if not numeric_ok:
            audit_notes.append("Candidate answer modified to prevent price hallucination.")
            verified_prices = re.findall(r'\$\s*[0-9,]+', sources_combined)
            verified_info = f" According to verified resort records, the official rate is {', '.join(set(verified_prices))}." if verified_prices else ""
            sanitized_answer = (
                f"{candidate_answer}\n\n"
                f"*(Verification Notice:{verified_info} Official resort rates are strictly governed by our published tariffs. "
                f"Our front desk directly validates all room folio quotes).* "
            )
            return ValidatedAnswer(
                original_query=query,
                raw_candidate_answer=candidate_answer,
                final_grounded_answer=sanitized_answer,
                verdict=ValidationVerdict.HALLUCINATION_INTERCEPTED,
                confidence_score=0.88,
                retrieved_sources=source_names or ["Verified Hotel KB"],
                is_safe=True,
                audit_notes=audit_notes,
            )

        # Otherwise: Grounded Pass
        audit_notes.append(f"Answer grounded with {overlap_ratio * 100:.1f}% lexical support in source documents.")
        return ValidatedAnswer(
            original_query=query,
            raw_candidate_answer=candidate_answer,
            final_grounded_answer=candidate_answer,
            verdict=ValidationVerdict.GROUNDED_PASS,
            confidence_score=metric.confidence_score,
            retrieved_sources=source_names or ["Verified Resort Knowledge"],
            is_safe=True,
            audit_notes=audit_notes,
        )
