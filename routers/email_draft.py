"""Email Draft Router — Tone-adapted negotiation emails from engine."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date
import models, database
from routers.dependencies import get_current_business
from routers.engine_bridge import db_to_business_state
from engine.constraint_detector import detect_constraints
from engine.rescheduling import generate_rescheduling_plan, _draft_message

class DraftRequest(BaseModel):
    obligation_id: int

router = APIRouter(prefix="/email", tags=["email"])

def _subject(biz: str, cp: str, ct: str) -> str:
    ct = (ct or "other").lower()
    if ct == "supplier": return f"Payment Extension Request - {biz}"
    if ct == "utility": return f"Service Payment Inquiry - {cp}"
    if ct in ("employee","salary"): return "Important: Upcoming Payroll Update"
    return f"Payment Update - {cp}"

def _tone(ct: str) -> str:
    ct = (ct or "other").lower()
    if ct in ("tax","gst","loan_emi","loan","government"): return "formal"
    if ct in ("employee","salary"): return "friendly"
    return "professional"

@router.post("/draft")
def generate_email(request: DraftRequest, business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    ob = db.query(models.Obligation).filter(
        models.Obligation.id == request.obligation_id,
        models.Obligation.business_id == business.id
    ).first()
    if not ob:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Obligation not found"})

    state = db_to_business_state(business, db)
    cr = detect_constraints(state)
    plan = generate_rescheduling_plan(state, cr)

    engine_draft = next((e for e in plan.entries if e.obligation_id == str(ob.id)), None)
    ct = ob.counterparty_type or "other"

    if engine_draft:
        subject = _subject(business.name, ob.counterparty, ct)
        body = engine_draft.draft_message
    else:
        tone = _tone(ct)
        subject = _subject(business.name, ob.counterparty, ct)
        body = _draft_message(ob.counterparty, ob.amount, ob.due_date, ob.due_date, tone, business.name)

    return {"draft_subject": subject, "draft_body": body}

@router.get("/drafts")
def get_all_drafts(business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    state = db_to_business_state(business, db)
    cr = detect_constraints(state)
    plan = generate_rescheduling_plan(state, cr)
    engine_drafts = {e.obligation_id: e for e in plan.entries}

    unpaid = db.query(models.Obligation).filter(
        models.Obligation.business_id == business.id, models.Obligation.is_paid == False
    ).all()

    drafts = []
    for ob in unpaid:
        ct = ob.counterparty_type or "other"
        subject = _subject(business.name, ob.counterparty, ct)
        oid = str(ob.id)
        if oid in engine_drafts:
            body = engine_drafts[oid].draft_message
        else:
            body = _draft_message(ob.counterparty, ob.amount, ob.due_date, ob.due_date, _tone(ct), business.name)
        drafts.append({
            "id": ob.id, "counterparty": ob.counterparty, "amount": ob.amount,
            "due_date": ob.due_date.isoformat(),
            "subject_preview": subject, "body_preview": body[:100] + "..." if len(body) > 100 else body,
        })
    return {"drafts": drafts}
