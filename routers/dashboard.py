"""
Dashboard Router — Powered by the financial engine.
All data comes from engine computations on real DB data.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
import models, database
from routers.dependencies import get_current_business
from routers.engine_bridge import db_to_business_state
from engine.liquidity import get_liquidity_summary
from engine.constraint_detector import detect_constraints
from engine.cot_explainer import explain_decisions

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    state = db_to_business_state(business, db)
    liquidity = get_liquidity_summary(state)
    constraint_report = detect_constraints(state)
    explanations = explain_decisions(constraint_report, state)

    # Build obligation summaries from engine's scored obligations
    obligation_summaries = []
    for scored in constraint_report.scored_obligations:
        obl = scored.obligation
        obligation_summaries.append({
            "id": obl.id,
            "counterparty": obl.counterparty_name,
            "counterparty_type": obl.type.value,
            "amount": obl.amount,
            "due_date": obl.due_date.isoformat(),
            "urgency": scored.urgency_contribution / 0.35 if scored.urgency_contribution else 0,
            "penalty_risk": scored.penalty_contribution / 0.30 if scored.penalty_contribution else 0,
            "priority_score": scored.priority_score,
            "rank": scored.rank,
            "can_pay": scored.can_pay,
        })

    receivable_summaries = [
        {"id": r.id, "counterparty": r.counterparty_name, "amount": r.amount,
         "expected_date": r.expected_date.isoformat(), "confidence": r.confidence}
        for r in state.receivables
    ]

    # 6-month runway chart from engine's daily projections
    today = date.today()
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    runway_chart = []
    for i in range(6):
        idx = (today.month - 1 + i) % 12
        if i == 0:
            runway_chart.append({"month": months[idx], "actual": liquidity.cash_balance})
        else:
            projected = 0.0
            target_day = i * 30
            for snap in liquidity.runway:
                if (snap.day - today).days >= target_day - 5:
                    projected = max(0, snap.closing_balance)
                    break
            if not projected and liquidity.runway:
                projected = max(0, liquidity.runway[-1].closing_balance)
            runway_chart.append({"month": months[idx], "projected": projected})

    daily_runway = [
        {"day": snap.day.isoformat(), "balance": round(snap.closing_balance, 2)}
        for snap in liquidity.runway
    ]

    explanation_dicts = [
        {"obligation_id": e.obligation_id, "obligation_name": e.obligation_name,
         "decision": e.decision, "cash_constraint": e.cash_constraint,
         "risk_comparison": e.risk_comparison, "tradeoff_justification": e.tradeoff_justification}
        for e in explanations
    ]

    return {
        "business_name": business.name,
        "currency": business.currency,
        "cash_balance": liquidity.cash_balance,
        "available_cash": liquidity.available_cash,
        "days_to_zero": liquidity.days_to_zero,
        "total_payables": liquidity.total_payables,
        "total_receivables": liquidity.total_receivables,
        "net_position": liquidity.net_position,
        "is_constrained": constraint_report.is_constrained,
        "shortfall": constraint_report.shortfall,
        "obligations": obligation_summaries,
        "receivables": receivable_summaries,
        "runway_chart": runway_chart,
        "daily_runway": daily_runway,
        "explanations": explanation_dicts,
    }
