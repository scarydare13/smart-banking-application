from pydantic import BaseModel, condecimal, constr
from typing import Literal


class AccountCreate(BaseModel):
    account_type: Literal["CURRENT", "SAVINGS", "FIXED_DEPOSIT"]  # only allowed values
    initial_deposit: condecimal(gt=0, max_digits=15, decimal_places=2)  # positive decimal


class AccountResponse(BaseModel):
    message: str
    account_id: int
    account_number: str
    account_type: str
    balance: condecimal(max_digits=15, decimal_places=2)
    created_at: str
