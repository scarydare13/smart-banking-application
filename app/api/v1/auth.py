from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.models.customer import Customer
from app.core.security import verify_password, create_access_token, get_password_hash
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a customer and return a JWT token
    """
    # Get user by email
    user = db.query(Customer).filter(Customer.email == data.email).first()
    if not user:
        logger.warning(f"Login failed - no user found: {data.email}")
        # Use generic message to prevent email enumeration
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not verify_password(data.password, user.password_hash):
        logger.warning(f"Login failed - invalid password for user: {user.customer_id}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if KYC is pending
    if user.kyc_status == "REJECTED":
        raise HTTPException(
            status_code=403, 
            detail="Account access denied. Please complete KYC verification."
        )

    # Create access token
    token_data = {
        "customer_id": user.customer_id,
        "email": user.email,
        "kyc_status": user.kyc_status
    }
    token = create_access_token(token_data)
    
    logger.info(f"Successful login for user {user.customer_id}")
    return {"access_token": token, "token_type": "bearer"}