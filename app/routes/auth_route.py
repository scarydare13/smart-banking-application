from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.customer import Customer
from app.schemas.auth import LoginRequest, TokenResponse, RegisterRequest
from app.core.security import verify_password, create_access_token
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Debug logging - REMOVE in production
    logger.debug(f"Login attempt: email={data.email}, password={data.password}")

    user = db.query(Customer).filter(Customer.email == data.email).first()
    if user is None:
    # No user found
        raise HTTPException(status_code=401, detail=" user is none")

    if not user or not verify_password(data.password, user.password_hash):
        logger.warning(f"Login failed for {data.email} with password={data.password}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": user.customer_id, "email": user.email})
    logger.info(f"User {user.customer_id} logged in successfully with email={data.email}")
    return {"customer_id": user.customer_id, "access_token": token, "token_type": "bearer"}

