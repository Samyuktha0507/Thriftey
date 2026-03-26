from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import models, database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
SECRET_KEY = "thriftey_secret_dev"
ALGORITHM = "HS256"

def get_current_business_id(token: str = Depends(oauth2_scheme)) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": "unauthorized", "message": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        business_id: int = payload.get("business_id")
        if business_id is None:
            raise credentials_exception
        return business_id
    except JWTError:
        raise credentials_exception

def get_current_business(business_id: int = Depends(get_current_business_id), db: Session = Depends(database.get_db)) -> models.Business:
    business = db.query(models.Business).filter(models.Business.id == business_id).first()
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": "Business not found"}
        )
    return business
