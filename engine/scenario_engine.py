"""
What-If Scenario Engine
───────────────────────
Applies a scenario modification to a BusinessState copy,
re-runs liquidity + constraint analysis, and computes deltas.

Supports:
  - Cash balance override
  - Delayed receivable
  - Removed obligation
  - Changed obligation amount/date
  - Added obligation

Pure Python. No LLM.
"""

from __future__ import annotations
from copy import deepcopy
from datetime import date

from schemas import BusinessState, WhatIfScenario, WhatIfResult
from engine.liquidity import get_liquidity_summary
from engine.constraint_detector import detect_constraints


def run_what_if(state: BusinessState, scenario: WhatIfScenario) -> WhatIfResult:
    """Run a what-if simulation and return the delta analysis."""
    # Original analysis
    orig_liquidity = get_liquidity_summary(state)
    orig_constraints = detect_constraints(state)

    # Deep copy for mutation
    modified = state.model_copy(deep=True)

    # ── Apply scenario modifications ──

    if scenario.cash_balance_override is not None:
        modified.cash_balance = scenario.cash_balance_override

    if scenario.delayed_receivable_id and scenario.delayed_receivable_new_date:
        for r in modified.receivables:
            if r.id == scenario.delayed_receivable_id:
                r.expected_date = scenario.delayed_receivable_new_date
                break

    if scenario.removed_obligation_id:
        modified.obligations = [
            ob for ob in modified.obligations
            if ob.id != scenario.removed_obligation_id
        ]

    if scenario.added_obligation:
        modified.obligations.append(scenario.added_obligation)

    if scenario.changed_obligation_id:
        for ob in modified.obligations:
            if ob.id == scenario.changed_obligation_id:
                if scenario.changed_obligation_amount is not None:
                    ob.amount = scenario.changed_obligation_amount
                if scenario.changed_obligation_date is not None:
                    ob.due_date = scenario.changed_obligation_date
                break

    # ── Re-analyze modified state ──
    new_liquidity = get_liquidity_summary(modified)
    new_constraints = detect_constraints(modified)

    delta_days = new_liquidity.days_to_zero - orig_liquidity.days_to_zero
    delta_shortfall = new_constraints.shortfall - orig_constraints.shortfall

    # Build impact summary
    impact_parts = []
    if delta_days != 0:
        direction = "improves" if delta_days > 0 or (new_liquidity.days_to_zero == -1 and orig_liquidity.days_to_zero >= 0) else "worsens"
        if new_liquidity.days_to_zero == -1:
            impact_parts.append(f"Runway {direction}: now solvent beyond projection horizon")
        else:
            impact_parts.append(f"Runway {direction} by {abs(delta_days)} days (now {new_liquidity.days_to_zero} days)")

    if abs(delta_shortfall) > 0.01:
        if delta_shortfall < 0:
            impact_parts.append(f"Shortfall decreases by ₹{abs(delta_shortfall):,.0f}")
        else:
            impact_parts.append(f"Shortfall increases by ₹{delta_shortfall:,.0f}")

    if not impact_parts:
        impact_parts.append("No significant financial impact detected")

    return WhatIfResult(
        scenario_description=scenario.description,
        original_days_to_zero=orig_liquidity.days_to_zero,
        new_days_to_zero=new_liquidity.days_to_zero,
        delta_days=delta_days,
        original_shortfall=orig_constraints.shortfall,
        new_shortfall=new_constraints.shortfall,
        delta_shortfall=round(delta_shortfall, 2),
        impact_summary=". ".join(impact_parts),
        new_constraint_report=new_constraints,
        new_liquidity=new_liquidity,
    )
