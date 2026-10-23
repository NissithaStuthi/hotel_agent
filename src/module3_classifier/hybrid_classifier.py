"""Module 3: Hybrid Classifier Ensemble

Fuses Vector Embedding Similarity and LLM/Semantic Parsing to maximize
accuracy across diverse guest phrasing.
"""

from src.module3_classifier.schemas import (
    IntentCategory,
    DomainCategory,
    UrgencyLevel,
    ClassificationResult
)
from src.module3_classifier.embedding_classifier import EmbeddingIntentClassifier
from src.module3_classifier.llm_classifier import LLMIntentClassifier


class HybridIntentClassifier:
    """Ensemble intent classifier."""

    def __init__(self):
        self.embedding_clf = EmbeddingIntentClassifier()
        self.llm_clf = LLMIntentClassifier()

    def classify(self, query: str) -> ClassificationResult:
        res_emb = self.embedding_clf.classify(query)
        res_llm = self.llm_clf.classify(query)

        # If both agree on intent and domain, high confidence
        if res_emb.intent_category == res_llm.intent_category and res_emb.domain == res_llm.domain:
            res_llm.confidence = min(0.99, res_llm.confidence + 0.05)
            res_llm.reasoning = f"Dual Consensus: Vector search and Semantic analysis matched '{res_emb.intent_category.value}'"
            return res_llm

        # Prioritize Emergency / Complaint from LLM/rules as safety critical
        if res_llm.intent_category in [IntentCategory.EMERGENCY, IntentCategory.COMPLAINT]:
            return res_llm

        # If embedding confidence is very high, use embedding result with LLM entities
        if res_emb.confidence > 0.85:
            res_emb.entities = res_llm.entities
            return res_emb

        return res_llm
