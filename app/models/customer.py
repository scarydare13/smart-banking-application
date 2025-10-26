from sqlalchemy import Column, BigInteger, String, TIMESTAMP, Date
from sqlalchemy.sql import func
from app.db.base import Base

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(BigInteger, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    phone_number = Column(String(15), unique=True)
    address = Column(String)
    kyc_status = Column(String(20), nullable=False, server_default="PENDING")  # PENDING/VERIFIED/REJECTED
    password_hash = Column(String(128), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
