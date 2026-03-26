"""What-If Router — Powered by the scenario engine. Deterministic simulation."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any
from datetime import date
import models, database
from routers.dependencies import get_current_business
from routers.engine_bridge import db_to_business_state
from schemas import WhatIfScenario
from engine.scenario_engine import run_what_if

class WhatIfRequest(BaseModel):
    variable: str
    id: Optional[int] = None
    new_value: Any

router = APIRouter(prefix="/whatif", tags=["whatif"])

@router.post("/")
def run_whatif_scenario(request: WhatIfRequest, business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    state = db_to_business_state(business, db)

    if request.variable == "cash_balance":
        scenario = WhatIfScenario(description=f"Change cash to ₹{float(request.new_value):,.0f}", cash_balance_override=float(request.new_value))
    elif request.variable == "obligation_amount":
        if not request.id:
            raise HTTPException(status_code=400, detail={"error": "bad_request", "message": "id required"})
        scenario = WhatIfScenario(description=f"Change obligation {request.id} to ₹{float(request.new_value):,.0f}",
                                  changed_obligation_id=str(request.id), changed_obligation_amount=float(request.new_value))
    elif request.variable == "receivable_date":
        if not request.id:
            raise HTTPException(status_code=400, detail={"error": "bad_request", "message": "id required"})
        scenario = WhatIfScenario(description=f"Delay receivable {request.id} to {request.new_value}",
                                  delayed_receivable_id=str(request.id), delayed_receivable_new_date=date.fromisoformat(str(request.new_value)))
    else:
        raise HTTPException(status_code=400, detail={"error": "bad_request", "message": "Invalid variable"})

    result = run_what_if(state, scenario)
    old_runway = result.original_days_to_zero if result.original_days_to_zero >= 0 else 999
    new_runway = result.new_days_to_zero if result.new_days_to_zero >= 0 else 999

    affected = [
        {"id": s.obligation.id, "counterparty": s.obligation.counterparty_name,
         "amount": s.obligation.amount, "due_date": s.obligation.due_date.isoformat()}
        for s in result.new_constraint_report.scored_obligations if s.can_pay in ("partial", "cannot_pay")
    ]

    trajectory = [{"day": i+1, "balance": round(max(0, snap.closing_balance), 2)} for i, snap in enumerate(result.new_liquidity.runway)]

    return {
        "old_runway_days": old_runway,
        "new_runway_days": new_runway,
        "delta_days": new_runway - old_runway,
        "affected_obligations": affected,
        "trajectory_chart": trajectory,
        "impact_summary": result.impact_summary,
    }
