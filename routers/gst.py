"""GST Router — Engine-powered standard Indian GST calendar."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
import models, database
from routers.dependencies import get_current_business
from engine.gst_reminders import get_upcoming_gst_deadlines

router = APIRouter(prefix="/gst", tags=["gst"])

@router.get("/reminders")
def get_gst_reminders(business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    today = date.today()
    engine_reminders = get_upcoming_gst_deadlines(today, 30)

    results = [
        {"form_name": r.form_name, "deadline_date": r.due_date.isoformat(),
         "days_remaining": r.days_until_due, "notes": r.description,
         "penalty_info": r.penalty_info, "is_overdue": r.is_overdue}
        for r in engine_reminders
    ]

    # Also include custom DB reminders
    db_reminders = db.query(models.GSTReminder).filter(models.GSTReminder.business_id == business.id).all()
    engine_forms = {r.form_name for r in engine_reminders}
    cutoff = today + timedelta(days=30)

    for rem in db_reminders:
        if rem.form_name in engine_forms:
            continue
        try:
            deadline = date(today.year, today.month, rem.deadline_day)
        except ValueError:
            continue
        if deadline < today:
            m, y = today.month + 1, today.year
            if m > 12: m, y = 1, y + 1
            try:
                deadline = date(y, m, rem.deadline_day)
            except ValueError:
                continue
        if today <= deadline <= cutoff:
            results.append({
                "form_name": rem.form_name,
                "deadline_date": deadline.isoformat(),
                "days_remaining": (deadline - today).days,
                "notes": rem.notes,
            })

    results.sort(key=lambda x: x["days_remaining"])
    return results
