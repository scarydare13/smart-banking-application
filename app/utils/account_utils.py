import datetime, random
from app.core.config import MIN_INITIAL_DEPOSIT

ALLOWED_TYPES = {"SAVINGS", "CURRENT", "FIXED_DEPOSIT"}

def generate_account_number(prefix="SB"):
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    rand = random.randint(100000, 999999)
    return f"{prefix}{today}{rand}"

def validate_account_type(t: str) -> str:
    if not t:
        raise ValueError("account_type missing")
    t_up = t.strip().upper()
    if t_up not in ALLOWED_TYPES:
        raise ValueError(f"Invalid account type: {t}")
    return t_up

def validate_initial_deposit(amount):
    if float(amount) < MIN_INITIAL_DEPOSIT:
        raise ValueError(f"Initial deposit must be >= {MIN_INITIAL_DEPOSIT}")
    return float(amount)
