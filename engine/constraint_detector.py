"""
Constraint Detector
───────────────────
Determines which obligations can/cannot be paid given available cash.
Walks through prioritized obligations in rank order, subtracting amounts
from available cash. Classifies each as payable / partial / cannot_pay.

FORMULA:
    shortfall = max(0, total_obligations - available_cash)
    is_constrained = shortfall > 0

No LLM. Pure arithmetic.
"""

from __future__ import annotations
from typing import List

from schemas import BusinessState, ConstraintReport, ScoredObligation
from engine.obligation_matrix import prioritize_obligations


def detect_constraints(state: BusinessState) -> ConstraintReport:
    """
    Classify each obligation as payable/partial/cannot_pay
    by walking the priority-sorted list and consuming available cash.
    """
    available = state.cash_balance - state.locked_cash
    total_obligations = sum(ob.amount for ob in state.obligations)
    shortfall = max(0.0, total_obligations - available)

    # Get prioritized obligations
    scored = prioritize_obligations(
        state.obligations, state.counterparties, state.as_of_date
    )

    remaining_cash = available
    payable_ids: List[str] = []
    conflict_ids: List[str] = []

    for s in scored:
        if remaining_cash >= s.obligation.amount:
            s.can_pay = "payable"
            remaining_cash -= s.obligation.amount
            s.cumulative_cash_after = round(remaining_cash, 2)
            payable_ids.append(s.obligation.id)
        elif remaining_cash > 0:
            s.can_pay = "partial"
            s.cumulative_cash_after = 0.0
            remaining_cash = 0.0
            conflict_ids.append(s.obligation.id)
        else:
            s.can_pay = "cannot_pay"
            s.cumulative_cash_after = 0.0
            conflict_ids.append(s.obligation.id)

    return ConstraintReport(
        available_cash=round(state.cash_balance - state.locked_cash, 2),
        total_obligations=round(total_obligations, 2),
        shortfall=round(shortfall, 2),
        scored_obligations=scored,
        payable_obligations=payable_ids,
        conflict_obligations=conflict_ids,
        is_constrained=shortfall > 0,
    )
