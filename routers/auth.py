from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import models, database
from pydantic import BaseModel
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "thriftey_secret_dev"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class RegisterRequest(BaseModel):
    business_name: str
    email: str
    password: str
    gst_number: Optional[str] = None
    currency: str = "INR"

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == request.email).first():
        raise HTTPException(status_code=400, detail={"error": "bad_request", "message": "Email already registered"})
    new_business = models.Business(
        name=request.business_name,
        gst_number=request.gst_number,
        currency=request.currency,
    )
    db.add(new_business)
    db.commit()
    db.refresh(new_business)
    new_user = models.User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        business_id=new_business.id,
    )
    db.add(new_user)
    db.commit()
    return {"message": "registered"}

@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail={"error": "unauthorized", "message": "Invalid credentials"})
    access_token = create_access_token(
        data={"sub": str(user.id), "business_id": user.business_id}
    )
    return {"access_token": access_token, "token_type": "bearer"}
