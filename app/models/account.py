from sqlalchemy import Column, BigInteger, String, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(BigInteger, primary_key=True, index=True)
    account_number = Column(String(20), unique=True, nullable=False, index=True)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    account_type = Column(String(20), nullable=False)  # SAVINGS/CURRENT/FIXED_DEPOSIT
    balance = Column(DECIMAL(15,2), nullable=False, server_default="0.00")
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    customer = relationship("Customer", backref="accounts")
