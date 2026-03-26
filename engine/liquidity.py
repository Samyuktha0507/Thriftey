"""
Liquidity & Runway Calculator
─────────────────────────────
FORMULA — Days to Zero:
    runway_days = project cash day-by-day, subtracting obligations
                  and adding receivables (adjusted by confidence).
    First day closing_balance < 0 → days_to_zero.
    If never negative within projection horizon → -1 (solvent).

No LLM. No API calls. Pure arithmetic.
"""

from __future__ import annotations
from datetime import date, timedelta
from typing import List

from schemas import BusinessState, DailySnapshot, LiquiditySummary


def compute_runway(state: BusinessState, projection_days: int = 30) -> List[DailySnapshot]:
    """Day-by-day cash projection for `projection_days` from as_of_date."""
    available = state.cash_balance - state.locked_cash
    snapshots: List[DailySnapshot] = []

    # Index obligations and receivables by date for O(1) lookup
    obl_by_date: dict[date, list] = {}
    for ob in state.obligations:
        obl_by_date.setdefault(ob.due_date, []).append(ob)

    rec_by_date: dict[date, list] = {}
    for r in state.receivables:
        rec_by_date.setdefault(r.expected_date, []).append(r)

    balance = available

    for day_offset in range(projection_days):
        current_day = state.as_of_date + timedelta(days=day_offset)
        opening = balance

        # Outflows: obligations due this day
        day_obligations = obl_by_date.get(current_day, [])
        outflows = sum(ob.amount for ob in day_obligations)
        obl_ids = [ob.id for ob in day_obligations]

        # Inflows: receivables expected this day (weighted by confidence)
        day_receivables = rec_by_date.get(current_day, [])
        inflows = sum(r.amount * r.confidence for r in day_receivables)
        rec_ids = [r.id for r in day_receivables]

        closing = opening + inflows - outflows
        balance = closing

        snapshots.append(DailySnapshot(
            day=current_day,
            opening_balance=round(opening, 2),
            inflows=round(inflows, 2),
            outflows=round(outflows, 2),
            closing_balance=round(closing, 2),
            obligations_due=obl_ids,
            receivables_due=rec_ids,
        ))

    return snapshots


def compute_days_to_zero(state: BusinessState, projection_days: int = 90) -> int:
    """
    Returns the day number (0-indexed) when closing_balance first goes negative.
    Returns -1 if solvent throughout the projection horizon.
    """
    runway = compute_runway(state, projection_days)
    for i, snap in enumerate(runway):
        if snap.closing_balance < 0:
            return i
    return -1


def get_liquidity_summary(state: BusinessState, projection_days: int = 30) -> LiquiditySummary:
    """High-level liquidity overview with daily runway."""
    runway = compute_runway(state, projection_days)
    days_to_zero = compute_days_to_zero(state, 90)

    available = state.cash_balance - state.locked_cash
    total_payables = sum(ob.amount for ob in state.obligations)
    total_receivables = sum(r.amount for r in state.receivables)
    net = available + total_receivables - total_payables

    return LiquiditySummary(
        cash_balance=state.cash_balance,
        available_cash=round(available, 2),
        total_payables=round(total_payables, 2),
        total_receivables=round(total_receivables, 2),
        net_position=round(net, 2),
        days_to_zero=days_to_zero,
        runway=runway,
    )
