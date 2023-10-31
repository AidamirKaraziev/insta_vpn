from sqlite3 import Timestamp
from typing import Optional
from pydantic import BaseModel, UUID4


class AccountGet(BaseModel):
    id: int
    name: Optional[str]
    number: Optional[str]
    created_at: Optional[Timestamp]
    trial_is_active: Optional[bool]
    referral_id: Optional[UUID4]
    can_pay_out: Optional[bool]


class AccountCreate(BaseModel):
    id: int
    name: Optional[str]
    number: Optional[str]
    referral_id: Optional[UUID4]


class AccountUpdate(BaseModel):
    name: Optional[str]
    number: Optional[str]
    trial_is_active: Optional[bool]
    can_pay_out: Optional[bool]
