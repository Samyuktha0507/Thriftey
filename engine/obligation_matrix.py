"""
Obligation Priority Matrix — 4-Factor Weighted Scoring
───────────────────────────────────────────────────────
FORMULA — Priority Score (0.0 → 1.0):
    priority = (urgency_w * urgency_norm)
             + (penalty_w * penalty_norm)
             + (relationship_w * relationship_norm)
             + (flexibility_w * flexibility_norm)

WEIGHTS:
    urgency       = 0.35
    penalty_risk  = 0.30
    relationship  = 0.20
    flexibility   = 0.15

Each factor is normalized to [0, 1].

Higher score = pay this first.
Pure Python. No LLM.
"""

from __future__ import annotations
from datetime import date
from typing import List

from schemas import (
    Obligation, CounterpartyProfile, ScoredObligation,
    Urgency, Flexibility, RelationshipType,
)

# ── Weights ──────────────────────────────────────────────────────────────
W_URGENCY = 0.35
W_PENALTY = 0.30
W_RELATIONSHIP = 0.20
W_FLEXIBILITY = 0.15

# ── Normalization Maps ──────────────────────────────────────────────────

URGENCY_SCORES = {
    Urgency.CRITICAL: 1.0,
    Urgency.HIGH: 0.8,
    Urgency.MEDIUM: 0.5,
    Urgency.LOW: 0.2,
}

FLEXIBILITY_SCORES = {
    Flexibility.NONE: 1.0,    # no flexibility → HIGH priority
    Flexibility.LOW: 0.75,
    Flexibility.MEDIUM: 0.4,
    Flexibility.HIGH: 0.1,
}

RELATIONSHIP_SCORES = {
    RelationshipType.GOVERNMENT: 1.0,
    RelationshipType.LENDER: 0.95,
    RelationshipType.EMPLOYEE: 0.85,
    RelationshipType.CRITICAL_SUPPLIER: 0.80,
    RelationshipType.LANDLORD: 0.70,
    RelationshipType.UTILITY_PROVIDER: 0.60,
    RelationshipType.REGULAR_SUPPLIER: 0.40,
    RelationshipType.OTHER: 0.30,
}


def _compute_urgency_from_date(ob: Obligation, as_of: date) -> Urgency:
    """Recompute urgency based on actual days until due."""
    days = (ob.due_date - as_of).days
    if days <= 0:
        return Urgency.CRITICAL
    elif days <= 3:
        return Urgency.HIGH
    elif days <= 7:
        return Urgency.MEDIUM
    return Urgency.LOW


def score_obligation(
    ob: Obligation,
    counterparties: List[CounterpartyProfile],
    as_of: date,
) -> ScoredObligation:
    """Score a single obligation using the 4-factor weighted matrix."""
    # Recompute urgency from date
    urgency = _compute_urgency_from_date(ob, as_of)
    urgency_norm = URGENCY_SCORES.get(urgency, 0.5)

    # Penalty risk: use penalty_rate (0-2 scale) → normalize to 0-1
    penalty_norm = min(ob.penalty_rate / 2.0, 1.0) if ob.penalty_rate else 0.0

    # Relationship: find counterparty profile
    cp = next((c for c in counterparties if c.id == ob.counterparty_id), None)
    if cp:
        relationship_norm = RELATIONSHIP_SCORES.get(cp.relationship, 0.3)
    else:
        relationship_norm = 0.3

    # Flexibility
    flexibility_norm = FLEXIBILITY_SCORES.get(ob.flexibility, 0.4)

    # Weighted sum
    u_contrib = round(W_URGENCY * urgency_norm, 4)
    p_contrib = round(W_PENALTY * penalty_norm, 4)
    r_contrib = round(W_RELATIONSHIP * relationship_norm, 4)
    f_contrib = round(W_FLEXIBILITY * flexibility_norm, 4)

    total = round(u_contrib + p_contrib + r_contrib + f_contrib, 4)

    return ScoredObligation(
        obligation=ob,
        priority_score=total,
        urgency_contribution=u_contrib,
        penalty_contribution=p_contrib,
        relationship_contribution=r_contrib,
        flexibility_contribution=f_contrib,
    )


def prioritize_obligations(
    obligations: List[Obligation],
    counterparties: List[CounterpartyProfile],
    as_of: date,
) -> List[ScoredObligation]:
    """Score and rank all obligations. Returns list sorted by priority (highest first)."""
    scored = [score_obligation(ob, counterparties, as_of) for ob in obligations]
    scored.sort(key=lambda s: s.priority_score, reverse=True)

    for i, s in enumerate(scored):
        s.rank = i + 1

    return scored
