"""Regras determinísticas de publicação de processos judiciais.

A presunção de inocência e o direito à informação pública são equilibrados.
Nunca afirmar culpa apenas pela existência de processo.
"""

import logging

logger = logging.getLogger(__name__)

# Identity confidence threshold for judicial (higher than news)
JUDICIAL_IDENTITY_MIN_CONFIDENCE = 0.98

# Categories requiring double review
DOUBLE_REVIEW_CATEGORIES = {"criminal", "public_integrity", "electoral_criminal"}

# Roles where the politician is NOT accused
NON_ACCUSED_ROLES = {"plaintiff", "victim", "witness", "attorney", "authority", "interested_party"}


class JudicialPublicationDecision:
    """Resultado da aplicação das regras de publicação judicial."""

    def __init__(self, can_publish: bool, requires_review: bool,
                 requires_double_review: bool, reasons: list[str]):
        self.can_publish = can_publish
        self.requires_review = requires_review
        self.requires_double_review = requires_double_review
        self.reasons = reasons


def apply_judicial_publication_rules(
    case_data: dict,
    party_data: dict,
) -> JudicialPublicationDecision:
    """
    Aplica regras determinísticas sobre dados judiciais.
    """
    reasons: list[str] = []
    can_publish = True
    requires_review = True  # ALWAYS require review for judicial
    requires_double_review = False

    secrecy = case_data.get("secrecy_level", 0)
    public_access = case_data.get("public_access", True)
    identity_confidence = party_data.get("identity_confidence", 0.0)
    role_normalized = party_data.get("role_normalized", "unknown")
    match_status = party_data.get("match_status", "pending")
    category = case_data.get("case_category", "unknown")
    outcome = case_data.get("normalized_outcome")

    # Rule 1: Secret cases → BLOCK
    if secrecy > 0 or not public_access:
        can_publish = False
        reasons.append("case_under_secrecy")
        return JudicialPublicationDecision(False, False, False, reasons)

    # Rule 2: Identity not confirmed → BLOCK
    if identity_confidence < JUDICIAL_IDENTITY_MIN_CONFIDENCE:
        can_publish = False
        reasons.append(f"identity_not_confirmed:{identity_confidence:.2f}")

    # Rule 3: Match not confirmed → BLOCK
    if match_status not in ("confirmed",):
        can_publish = False
        reasons.append(f"match_not_confirmed:{match_status}")

    # Rule 4: Politician is plaintiff → different presentation
    if role_normalized in NON_ACCUSED_ROLES:
        reasons.append(f"non_accused_role:{role_normalized}")
        # Can still publish, but presentation must be different

    # Rule 5: Criminal/integrity → double review
    if category in DOUBLE_REVIEW_CATEGORIES:
        requires_double_review = True
        reasons.append(f"double_review_required:{category}")

    # Rule 6: Conviction → must specify if appealable
    if outcome and "convicted" in outcome:
        requires_double_review = True
        reasons.append("conviction_requires_appeal_info")

    # Rule 7: Charge filed ≠ convicted (guard)
    if outcome in ("charge_accepted",) and case_data.get("display_as_convicted"):
        can_publish = False
        reasons.append("charge_not_conviction_violation")

    # Rule 8: Unknown role → review
    if role_normalized == "unknown":
        reasons.append("unknown_role")

    # Rule 9: No source URL → block
    if not case_data.get("source_url"):
        can_publish = False
        reasons.append("no_source_url")

    return JudicialPublicationDecision(
        can_publish=can_publish,
        requires_review=requires_review,
        requires_double_review=requires_double_review,
        reasons=reasons,
    )
