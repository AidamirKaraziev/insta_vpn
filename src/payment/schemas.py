from typing import Optional
from pydantic import BaseModel, UUID4
from sqlite3 import Timestamp

from config import STATUS_CREATE, PAYMENT_TYPE_DECREASE
from payment_type.schemas import PaymentTypeGet
from status.schemas import StatusGet


class PaymentGet(BaseModel):
    id: UUID4
    referent_id: Optional[UUID4]
    amount: int
    spb_number: Optional[str]
    card_number: Optional[str]
    created_at: Optional[Timestamp]
    payment_type: Optional[PaymentTypeGet]
    status: Optional[StatusGet]


class PaymentCreate(BaseModel):
    id: Optional[UUID4] = None
    referent_id: UUID4
    amount: int
    spb_number: Optional[str]
    card_number: Optional[str]
    payment_type_id: int = PAYMENT_TYPE_DECREASE.id
    status_id: Optional[int] = STATUS_CREATE.id


class PaymentUpdate(BaseModel):
    status_id: Optional[int]
