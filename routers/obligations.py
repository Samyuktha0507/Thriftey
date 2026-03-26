"""Obligations Router — Engine-powered prioritization and conflict detection."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
import models, database
from routers.dependencies import get_current_business
from routers.engine_bridge import db_to_business_state
from engine.constraint_detector import detect_constraints

router = APIRouter(prefix="/obligations", tags=["obligations"])

@router.get("/")
def get_all_obligations(business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    state = db_to_business_state(business, db)
    constraint_report = detect_constraints(state)
    return [
        {
            "id": s.obligation.id,
            "counterparty": s.obligation.counterparty_name,
            "counterparty_type": s.obligation.type.value,
            "amount": s.obligation.amount,
            "due_date": s.obligation.due_date.isoformat(),
            "penalty_risk": s.penalty_contribution / 0.30 if s.penalty_contribution else 0,
            "urgency": s.urgency_contribution / 0.35 if s.urgency_contribution else 0,
            "priority_score": s.priority_score,
            "rank": s.rank,
            "can_pay": s.can_pay,
            "flexibility": s.flexibility_contribution / 0.15 if s.flexibility_contribution else 0,
            "is_paid": False,
        }
        for s in constraint_report.scored_obligations
    ]

@router.get("/conflicts")
def get_conflicts(business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    state = db_to_business_state(business, db)
    constraint_report = detect_constraints(state)
    today = date.today()
    weekly = [s for s in constraint_report.scored_obligations if s.obligation.due_date <= today + timedelta(days=7)]
    return {
        "conflict": constraint_report.is_constrained,
        "cash_balance": constraint_report.available_cash,
        "total_due_this_week": sum(s.obligation.amount for s in weekly),
        "shortfall": constraint_report.shortfall,
        "obligations": [
            {"id": s.obligation.id, "counterparty": s.obligation.counterparty_name,
             "amount": s.obligation.amount, "due_date": s.obligation.due_date.isoformat(),
             "can_pay": s.can_pay, "rank": s.rank}
            for s in weekly
        ]
    }
