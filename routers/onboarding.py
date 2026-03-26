"""Onboarding Router — Business profile setup."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import models, database
from routers.dependencies import get_current_business
from utils.crypto import encrypt_sensitive_string, decrypt_sensitive_string
from sqlalchemy.orm import Session

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

class BusinessOnboarding(BaseModel):
    name: str
    gst_number: str
    currency: Optional[str] = "INR"

@router.get("/status")
def onboarding_status(business: models.Business = Depends(get_current_business)):
    gst = decrypt_sensitive_string(business.gst_number) if business.gst_number else None
    return {"completed": business.onboarding_completed, "business_name": business.name, "gst_number": gst, "currency": business.currency}

@router.post("/complete")
def complete_onboarding(request: BusinessOnboarding, business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    business.name = request.name
    business.gst_number = encrypt_sensitive_string(request.gst_number)
    business.currency = request.currency
    business.onboarding_completed = True
    db.commit()
    return {"message": "Onboarding completed", "business_name": business.name}
