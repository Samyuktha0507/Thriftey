"""
Engine Bridge — Converts SQLAlchemy DB models to engine's BusinessState.
This is the integration layer between the database and the computation engine.
"""

from __future__ import annotations
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

import models
from schemas import (
    BusinessState, Obligation as EngineObligation, Receivable as EngineReceivable,
    CounterpartyProfile, ObligationType, Flexibility, RelationshipType, Urgency,
)

# ── Type Mappings ────────────────────────────────────────────────────────
TYPE_TO_OBLIGATION = {
    "supplier": ObligationType.SUPPLIER,
    "rent": ObligationType.RENT,
    "salary": ObligationType.SALARY,
    "employee": ObligationType.SALARY,
    "utility": ObligationType.UTILITY,
    "loan_emi": ObligationType.LOAN_EMI,
    "loan": ObligationType.LOAN_EMI,
    "tax": ObligationType.TAX,
    "gst": ObligationType.GST,
    "government": ObligationType.TAX,
    "insurance": ObligationType.INSURANCE,
    "other": ObligationType.OTHER,
}

TYPE_TO_RELATIONSHIP = {
    "supplier": RelationshipType.REGULAR_SUPPLIER,
    "rent": RelationshipType.LANDLORD,
    "salary": RelationshipType.EMPLOYEE,
    "employee": RelationshipType.EMPLOYEE,
    "utility": RelationshipType.UTILITY_PROVIDER,
    "loan_emi": RelationshipType.LENDER,
    "loan": RelationshipType.LENDER,
    "tax": RelationshipType.GOVERNMENT,
    "gst": RelationshipType.GOVERNMENT,
    "government": RelationshipType.GOVERNMENT,
    "insurance": RelationshipType.OTHER,
    "other": RelationshipType.OTHER,
}

TYPE_TO_FLEXIBILITY = {
    "supplier": Flexibility.MEDIUM,
    "rent": Flexibility.LOW,
    "salary": Flexibility.LOW,
    "employee": Flexibility.LOW,
    "utility": Flexibility.LOW,
    "loan_emi": Flexibility.NONE,
    "loan": Flexibility.NONE,
    "tax": Flexibility.NONE,
    "gst": Flexibility.NONE,
    "government": Flexibility.NONE,
    "insurance": Flexibility.MEDIUM,
    "other": Flexibility.HIGH,
}


def db_to_business_state(business: models.Business, db: Session, as_of: Optional[date] = None) -> BusinessState:
    """Convert DB models into the engine's BusinessState."""
    if as_of is None:
        as_of = date.today()

    # Cash balance
    cash_pos = db.query(models.CashPosition).filter(
        models.CashPosition.business_id == business.id
    ).order_by(models.CashPosition.as_of_date.desc()).first()
    cash_balance = cash_pos.balance if cash_pos else 0.0

    # Obligations
    db_obligations = db.query(models.Obligation).filter(
        models.Obligation.business_id == business.id,
        models.Obligation.is_paid == False
    ).all()

    engine_obligations = []
    counterparties = []
    seen_cp = set()

    for ob in db_obligations:
        ct_str = (ob.counterparty_type or "other").lower()
        ob_type = TYPE_TO_OBLIGATION.get(ct_str, ObligationType.OTHER)
        flexibility = TYPE_TO_FLEXIBILITY.get(ct_str, Flexibility.MEDIUM)

        days_until = (ob.due_date - as_of).days
        if days_until <= 0:
            urgency = Urgency.CRITICAL
        elif days_until <= 3:
            urgency = Urgency.HIGH
        elif days_until <= 7:
            urgency = Urgency.MEDIUM
        else:
            urgency = Urgency.LOW

        penalty_rate = ob.penalty_risk * 2.0 if ob.penalty_risk else 0.0
        cp_id = f"cp_{ob.counterparty.lower().replace(' ', '_')}"

        engine_obligations.append(EngineObligation(
            id=str(ob.id),
            counterparty_id=cp_id,
            counterparty_name=ob.counterparty,
            type=ob_type,
            amount=ob.amount,
            due_date=ob.due_date,
            urgency=urgency,
            flexibility=flexibility,
            penalty_rate=penalty_rate,
        ))

        if cp_id not in seen_cp:
            seen_cp.add(cp_id)
            relationship = TYPE_TO_RELATIONSHIP.get(ct_str, RelationshipType.OTHER)
            tone = "formal" if relationship in (RelationshipType.GOVERNMENT, RelationshipType.LENDER) else "friendly" if relationship == RelationshipType.EMPLOYEE else "professional"
            counterparties.append(CounterpartyProfile(
                id=cp_id, name=ob.counterparty, relationship=relationship,
                flexibility=flexibility, communication_tone=tone,
            ))

    # Receivables
    db_receivables = db.query(models.Receivable).filter(
        models.Receivable.business_id == business.id,
        models.Receivable.is_received == False
    ).all()

    engine_receivables = [
        EngineReceivable(
            id=str(r.id),
            counterparty_id=f"cp_{r.counterparty.lower().replace(' ', '_')}",
            counterparty_name=r.counterparty,
            amount=r.amount,
            expected_date=r.expected_date,
            confidence=r.confidence if r.confidence else 0.8,
        )
        for r in db_receivables
    ]

    return BusinessState(
        business_name=business.name,
        as_of_date=as_of,
        cash_balance=cash_balance,
        obligations=engine_obligations,
        receivables=engine_receivables,
        counterparties=counterparties,
        gst_registered=bool(business.gst_number),
    )
