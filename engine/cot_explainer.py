"""
Chain-of-Thought Explainer
──────────────────────────
Generates structured, human-readable reasoning for each obligation's
prioritization decision. Uses deterministic logic — the CoT is built
from the computed scores and constraint status, NOT from an LLM.

Output format per obligation:
    - Key factors considered
    - Why this obligation was prioritized
    - Trade-offs made
"""

from __future__ import annotations
from typing import List

from schemas import (
    BusinessState, ConstraintReport, ExplanationStep,
    ScoredObligation, Urgency,
)


def _explain_one(
    scored: ScoredObligation,
    available_cash: float,
    total_obligations: float,
    is_constrained: bool,
) -> ExplanationStep:
    """Build a structured explanation for one scored obligation."""
    ob = scored.obligation

    # Decision
    if scored.can_pay == "payable":
        decision = f"PAY — ₹{ob.amount:,.0f} to {ob.counterparty_name}. Sufficient cash available."
    elif scored.can_pay == "partial":
        decision = f"PARTIAL — ₹{ob.amount:,.0f} to {ob.counterparty_name}. Cash partially covers this obligation."
    else:
        decision = f"DEFER — ₹{ob.amount:,.0f} to {ob.counterparty_name}. Insufficient cash after higher-priority obligations."

    # Cash constraint context
    if is_constrained:
        deficit = total_obligations - available_cash
        cash_constraint = (
            f"Total obligations (₹{total_obligations:,.0f}) exceed available cash "
            f"(₹{available_cash:,.0f}) by ₹{deficit:,.0f}. "
            f"This obligation is ranked #{scored.rank} of {int(total_obligations > 0)}+ by priority."
        )
    else:
        cash_constraint = (
            f"Available cash (₹{available_cash:,.0f}) covers all obligations "
            f"(₹{total_obligations:,.0f}). No conflict."
        )

    # Risk comparison
    risk_parts = []
    if scored.urgency_contribution >= 0.28:  # 0.35 * 0.8
        risk_parts.append("HIGH urgency — due very soon or overdue")
    elif scored.urgency_contribution >= 0.175:
        risk_parts.append("MEDIUM urgency")
    else:
        risk_parts.append("LOW urgency — due date is distant")

    if scored.penalty_contribution >= 0.21:  # 0.30 * 0.7
        risk_parts.append("significant penalty risk")
    elif scored.penalty_contribution >= 0.09:
        risk_parts.append("moderate penalty risk")
    else:
        risk_parts.append("low penalty risk")

    if scored.relationship_contribution >= 0.16:  # 0.20 * 0.8
        risk_parts.append("critical relationship (government/lender/employee)")
    else:
        risk_parts.append("standard relationship")

    risk_comparison = "; ".join(risk_parts)

    # Trade-off justification
    if scored.can_pay == "payable":
        tradeoff = (
            f"Paying {ob.counterparty_name} (rank #{scored.rank}, score {scored.priority_score:.2f}) "
            f"leaves ₹{scored.cumulative_cash_after:,.0f} for remaining obligations."
        )
    elif scored.can_pay == "partial":
        tradeoff = (
            f"{ob.counterparty_name} ranked #{scored.rank} but cash is exhausted at this point. "
            f"Higher-priority obligations were funded first based on urgency, penalty, and relationship factors."
        )
    else:
        tradeoff = (
            f"Deferring {ob.counterparty_name} (rank #{scored.rank}) because "
            f"obligations ranked #1–#{scored.rank - 1} consumed all available cash. "
            f"This obligation scores {scored.priority_score:.2f} — lower than funded ones."
        )

    return ExplanationStep(
        obligation_id=ob.id,
        obligation_name=ob.counterparty_name,
        decision=decision,
        cash_constraint=cash_constraint,
        risk_comparison=risk_comparison,
        tradeoff_justification=tradeoff,
    )


def explain_decisions(
    constraint_report: ConstraintReport,
    state: BusinessState,
) -> List[ExplanationStep]:
    """Generate structured CoT explanations for all obligations."""
    return [
        _explain_one(
            scored,
            constraint_report.available_cash,
            constraint_report.total_obligations,
            constraint_report.is_constrained,
        )
        for scored in constraint_report.scored_obligations
    ]
