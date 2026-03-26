"""
Financial Health Score — 5-Factor Deterministic Scoring
───────────────────────────────────────────────────────
FORMULA — Total Score (0-100):
    total = payment_timeliness (max 30)
          + runway_buffer      (max 25)
          + gst_compliance     (max 20)
          + receivable_collect (max 15)
          + cash_reserve       (max 10)

Each component has a transparent sub-formula documented below.
No LLM. Pure arithmetic.
"""

from __future__ import annotations
from schemas import BusinessState, HealthScoreResult
from engine.liquidity import compute_days_to_zero


def compute_health_score(
    state: BusinessState,
    payment_history: dict,
) -> HealthScoreResult:
    """
    Compute deterministic health score from state + payment history.

    payment_history dict keys:
        total_obligations_last_90_days: int
        paid_on_time: int
        paid_late: int
        missed: int
        gst_filings_due_last_90_days: int
        gst_filed_on_time: int
        average_receivable_delay_days: float
    """
    factors = []
    tips = []

    # ── 1. Payment Timeliness (max 30) ──
    # Formula: (paid_on_time / total) * 30
    total_obl = max(payment_history.get("total_obligations_last_90_days", 1), 1)
    paid_on_time = payment_history.get("paid_on_time", 0)
    paid_late = payment_history.get("paid_late", 0)
    missed = payment_history.get("missed", 0)

    on_time_ratio = paid_on_time / total_obl
    # Penalize late payments (halved weight) and missed (zero weight)
    effective_ratio = (paid_on_time + paid_late * 0.5) / total_obl
    payment_score = round(min(effective_ratio * 30, 30), 2)

    factors.append(f"Payment timeliness: {paid_on_time}/{total_obl} on time ({on_time_ratio*100:.0f}%)")
    if on_time_ratio < 0.7:
        tips.append("Improve payment timeliness — pay at least 70% of obligations on time")
    if missed > 0:
        factors.append(f"Warning: {missed} missed payment(s) in last 90 days")
        tips.append(f"Clear {missed} overdue obligation(s) to boost score")

    # ── 2. Runway Buffer (max 25) ──
    # Formula: min(days_to_zero / 30, 1.0) * 25
    # 30+ days = full score, 0 days = zero
    d2z = compute_days_to_zero(state)
    if d2z == -1:
        runway_score = 25.0  # Solvent beyond horizon = max
        factors.append("Runway buffer: Solvent beyond 90-day horizon — excellent")
    else:
        ratio = min(d2z / 30.0, 1.0)
        runway_score = round(ratio * 25, 2)
        factors.append(f"Runway buffer: {d2z} days of cash runway")
        if d2z < 14:
            tips.append(f"Critical: Only {d2z} days of runway — consider reducing expenses or accelerating receivables")
        elif d2z < 30:
            tips.append("Build runway buffer to 30+ days for financial stability")

    # ── 3. GST Compliance (max 20) ──
    # Formula: (filed_on_time / filings_due) * 20
    gst_due = max(payment_history.get("gst_filings_due_last_90_days", 1), 1)
    gst_filed = payment_history.get("gst_filed_on_time", 0)
    gst_ratio = min(gst_filed / gst_due, 1.0)
    gst_score = round(gst_ratio * 20, 2)

    factors.append(f"GST compliance: {gst_filed}/{gst_due} filings on time ({gst_ratio*100:.0f}%)")
    if gst_ratio < 1.0:
        tips.append("File all pending GST returns to avoid ₹50/day penalty")

    # ── 4. Receivable Collection (max 15) ──
    # Formula: based on average delay and overdue count
    avg_delay = payment_history.get("average_receivable_delay_days", 0)
    overdue_receivables = [r for r in state.receivables if r.expected_date < state.as_of_date]
    overdue_count = len(overdue_receivables)

    if avg_delay <= 0:
        recv_score = 15.0
    elif avg_delay <= 7:
        recv_score = 12.0
    elif avg_delay <= 14:
        recv_score = 8.0
    elif avg_delay <= 30:
        recv_score = 4.0
    else:
        recv_score = 1.0

    # Penalize for each overdue receivable
    recv_score = max(0, recv_score - overdue_count * 2)
    recv_score = round(min(recv_score, 15), 2)

    factors.append(f"Receivable collection: avg delay {avg_delay:.0f} days, {overdue_count} overdue")
    if overdue_count > 0:
        overdue_total = sum(r.amount for r in overdue_receivables)
        tips.append(f"Follow up on {overdue_count} overdue receivable(s) totalling ₹{overdue_total:,.0f}")

    # ── 5. Cash Reserve Ratio (max 10) ──
    # Formula: (available_cash / monthly_obligations) * 10, capped at 10
    monthly_obligations = sum(ob.amount for ob in state.obligations)
    available = state.cash_balance - state.locked_cash
    if monthly_obligations > 0:
        reserve_ratio = available / monthly_obligations
        cash_score = round(min(reserve_ratio * 10, 10), 2)
    else:
        cash_score = 10.0

    factors.append(f"Cash reserve ratio: ₹{available:,.0f} / ₹{monthly_obligations:,.0f} obligations ({reserve_ratio*100:.0f}% coverage)" if monthly_obligations > 0 else "No outstanding obligations — full cash reserve score")
    if monthly_obligations > 0 and reserve_ratio < 0.5:
        tips.append("Cash reserves below 50% of obligations — increase savings buffer")

    # ── Total ──
    total = round(payment_score + runway_score + gst_score + recv_score + cash_score, 2)
    total = min(total, 100)

    return HealthScoreResult(
        total_score=total,
        payment_timeliness_score=payment_score,
        runway_buffer_score=runway_score,
        gst_compliance_score=gst_score,
        receivable_collection_score=recv_score,
        cash_reserve_score=cash_score,
        contributing_factors=factors,
        improvement_tips=tips,
    )
