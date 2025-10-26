from datetime import datetime

from app.core.smpt_mail import send_account_email
year = str(datetime.utcnow().year)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.customer import Customer
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse
from app.utils.logger import logger
from app.core.security import get_current_user

router = APIRouter(prefix="/accounts", tags=["accounts"])

# Minimum deposit mapping per account type
MIN_DEPOSIT = {
    "CURRENT": 500,
    "SAVINGS": 5000,
    "FIXED_DEPOSIT": 10000
}



def generate_account_number(db: Session, account_type: str):
    """
    Generate a professional-looking account number:
    Format: <TYPE_CODE><YYYY><6-digit serial>
    Example: SAV2025000123
    """
    #  Type prefix: first 3 letters of account type
    type_prefix = account_type[:3].upper()

    #  Year
    year = str(datetime.utcnow().year)

    #  Serial number: get last account of this type
    last_account = (
        db.query(Account)
        .filter(Account.account_type == account_type)
        .order_by(Account.account_id.desc())
        .first()
    )
    if last_account:
        # Extract numeric part from last account_number
        last_serial = int(last_account.account_number[-6:])
        new_serial = str(last_serial + 1).zfill(6)
    else:
        new_serial = "000001"

    #  Combine
    return f"{type_prefix}{year}{new_serial}"

@router.post("/create", response_model=dict)
def create_account(
    data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        #  Fetch customer
        customer = db.query(Customer).filter(Customer.customer_id == current_user["user_id"]).first()
        if not customer:
            logger.warning(f"Account creation failed - customer not found: {current_user['user_id']}")
            return {"status": "failed", "data": {}, "msg": "Customer not found"}

        if customer.kyc_status != "VERIFIED":
            logger.warning(f"Account creation failed - KYC not verified for {current_user['user_id']}")
            return {"status": "failed", "data": {}, "msg": "KYC not completed"}

        #  Validate account type
        acc_type = data.account_type.upper()
        if acc_type not in MIN_DEPOSIT:
            return {
                "status": "failed",
                "data": {},
                "msg": f"Invalid account type. Choose from {list(MIN_DEPOSIT.keys())}"
            }

        #  Validate initial deposit
        if data.initial_deposit < MIN_DEPOSIT[acc_type]:
            return {
                "status": "failed",
                "data": {},
                "msg": f"Minimum deposit for {acc_type} account is {MIN_DEPOSIT[acc_type]}"
            }

        #  Check duplicate account type
        existing = db.query(Account).filter(
            Account.customer_id == current_user["user_id"],
            Account.account_type == acc_type
        ).first()
        if existing:
            return {
                "status": "failed",
                "data": {},
                "msg": f"{acc_type} account already exists for this customer"
            }

        #  Create account
        acc_number = generate_account_number(db, acc_type)
        new_acc = Account(
            account_number=acc_number,
            customer_id=current_user["user_id"],
            account_type=acc_type,
            balance=data.initial_deposit
        )
        db.add(new_acc)
        db.commit()
        db.refresh(new_acc)

        #  Send email
        send_account_email(
            to_email=customer.email,
            customer_name=customer.full_name,
            account_number=new_acc.account_number,
            account_type=new_acc.account_type,
            balance=new_acc.balance
        )

        logger.info(f"Account {new_acc.account_number} ({acc_type}) created for customer {customer.full_name}")

        return {
            "status": "success",
            "data": {
                "account_id": new_acc.account_id,
                "account_number": new_acc.account_number,
                "account_type": new_acc.account_type,
                "balance": new_acc.balance,
                "customer_name": customer.full_name,
                "created_at": str(new_acc.created_at)
            },
            "msg": "Account created successfully"
        }

    except Exception as e:
        logger.error(f"Error creating account for user {current_user['user_id']}: {e}", exc_info=True)
        return {"status": "failed", "data": {}, "msg": "Internal server error"}
