"""Regras determinísticas de publicação de notícias.

A decisão final de publicação NÃO depende apenas da IA.
Estas regras são aplicadas APÓS a classificação.
"""

import logging

logger = logging.getLogger(__name__)

# Categories that ALWAYS require human review
MANDATORY_REVIEW_CATEGORIES = {
    "judicial", "investigation", "corruption",
}

# Fact types that prevent auto-publication
SENSITIVE_FACT_TYPES = {
    "charge_filed", "charge_accepted", "defendant",
    "conviction_first_instance", "conviction_appealable", "final_conviction",
    "allegation",
}

# Minimum confidence for auto-publish
MIN_CONFIDENCE_AUTO_PUBLISH = 0.92
MIN_IDENTITY_CONFIDENCE = 0.95


class PublicationDecision:
    """Resultado da aplicação das regras de publicação."""

    def __init__(self, can_publish: bool, requires_review: bool, reasons: list[str]):
        self.can_publish = can_publish
        self.requires_review = requires_review
        self.reasons = reasons


def apply_publication_rules(classification: dict) -> PublicationDecision:
    """
    Aplica regras determinísticas sobre o resultado da IA.
    Retorna decisão de publicação.
    """
    reasons: list[str] = []
    requires_review = False
    can_publish = True

    category = classification.get("category", "")
    fact_type = classification.get("fact_type", "")
    confidence = classification.get("confidence", 0.0)
    identity_conf = classification.get("identity_confidence", 0.0)
    impact = classification.get("reputational_impact", "")
    evidence = classification.get("evidence", [])
    summary = classification.get("summary", "")

    # Rule 1: Sensitive category → review
    if category in MANDATORY_REVIEW_CATEGORIES:
        requires_review = True
        reasons.append(f"sensitive_category:{category}")

    # Rule 2: Sensitive fact type → review
    if fact_type in SENSITIVE_FACT_TYPES:
        requires_review = True
        reasons.append(f"sensitive_fact_type:{fact_type}")

    # Rule 3: Low confidence → review
    if confidence < MIN_CONFIDENCE_AUTO_PUBLISH:
        requires_review = True
        reasons.append(f"low_confidence:{confidence:.2f}")

    # Rule 4: Identity uncertain → block
    if identity_conf < MIN_IDENTITY_CONFIDENCE:
        can_publish = False
        requires_review = True
        reasons.append(f"identity_uncertain:{identity_conf:.2f}")

    # Rule 5: No evidence → reject
    if not evidence:
        can_publish = False
        requires_review = True
        reasons.append("no_evidence")

    # Rule 6: Investigation ≠ conviction (guard)
    if fact_type == "investigation" and impact == "very_negative":
        requires_review = True
        reasons.append("investigation_impact_mismatch")

    # Rule 7: Acquittal should not be negative without justification
    if fact_type == "acquittal" and impact == "negative":
        requires_review = True
        reasons.append("acquittal_negative_review")

    # Rule 8: No source URL → block
    if not classification.get("source_url"):
        # This is checked at article level, not classification
        pass

    # Rule 9: Empty summary → review
    if not summary or len(summary) < 10:
        requires_review = True
        reasons.append("empty_or_short_summary")

    if requires_review:
        can_publish = False  # If review required, don't auto-publish

    return PublicationDecision(
        can_publish=can_publish and not requires_review,
        requires_review=requires_review,
        reasons=reasons,
    )
