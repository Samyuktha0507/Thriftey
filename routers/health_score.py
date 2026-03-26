"""Health Score Router — Engine-powered 5-factor scoring + gamification."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
import models, database
from routers.dependencies import get_current_business
from routers.engine_bridge import db_to_business_state
from engine.health_score import compute_health_score
from engine.gamification import get_gamification_status

router = APIRouter(prefix="/health-score", tags=["health_score"])

def _build_payment_history(business_id: int, db: Session) -> dict:
    today = date.today()
    ninety_ago = today - timedelta(days=90)
    all_ob = db.query(models.Obligation).filter(
        models.Obligation.business_id == business_id,
        models.Obligation.due_date >= ninety_ago,
    ).all()
    total = max(len(all_ob), 1)
    paid = sum(1 for o in all_ob if o.is_paid)
    missed = total - paid

    receivables = db.query(models.Receivable).filter(
        models.Receivable.business_id == business_id,
        models.Receivable.is_received == False,
    ).all()
    overdue_days = [(today - r.expected_date).days for r in receivables if r.expected_date < today]
    avg_delay = sum(overdue_days) / len(overdue_days) if overdue_days else 0

    return {
        "total_obligations_last_90_days": total,
        "paid_on_time": paid, "paid_late": 0, "missed": missed,
        "gst_filings_due_last_90_days": 6, "gst_filed_on_time": 6,
        "average_receivable_delay_days": avg_delay,
    }

@router.get("/")
def get_health_score(business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    state = db_to_business_state(business, db)
    payment_history = _build_payment_history(business.id, db)
    score_result = compute_health_score(state, payment_history)
    gamification = get_gamification_status(score_result)

    factors = {
        "payment_score": round(score_result.payment_timeliness_score * (40/30), 2),
        "gst_score": round(score_result.gst_compliance_score, 2),
        "runway_score": round(score_result.runway_buffer_score * (20/25), 2),
        "receivables_score": round((score_result.receivable_collection_score + score_result.cash_reserve_score) * (20/25), 2),
    }
    total = int(round(score_result.total_score))

    # Save to DB
    new_hs = models.HealthScore(
        business_id=business.id, score=total, level=gamification.level_name,
        factors=factors, badge_unlocked=len(gamification.unlocked_badges) > 0,
        next_unlock_condition=gamification.motivational_message,
    )
    db.add(new_hs)
    db.commit()

    return {
        "score": total, "level": gamification.level_name, "factors": factors,
        "badge_unlocked": len(gamification.unlocked_badges) > 0,
        "next_unlock_condition": gamification.motivational_message,
        "contributing_factors": score_result.contributing_factors,
        "improvement_tips": score_result.improvement_tips,
        "gamification": {
            "level_name": gamification.level_name,
            "level_number": gamification.level_number,
            "next_level_threshold": gamification.next_level_threshold,
            "badges": [{"id":b.id,"name":b.name,"description":b.description,"icon":b.icon,"unlocked":b.unlocked} for b in gamification.badges],
            "unlocked_badges": gamification.unlocked_badges,
            "motivational_message": gamification.motivational_message,
        },
    }
