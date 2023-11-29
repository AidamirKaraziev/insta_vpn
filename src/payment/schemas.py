from typing import Optional
from pydantic import BaseModel, UUID4
from sqlite3 import Timestamp

from status.schemas import StatusGet


class PaymentGet(BaseModel):
    id: UUID4
    referent_id: Optional[UUID4]
    amount: int
    spb_number: Optional[str]
    card_number: Optional[str]
    created_at: Optional[Timestamp]
    status: Optional[StatusGet]


class PaymentCreate(BaseModel):
    id: Optional[UUID4] = None
    referent_id: UUID4
    amount: int
    spb_number: Optional[str]
    card_number: Optional[str]
    status_id: Optional[int] = 1


class PaymentUpdate(BaseModel):
    status_id: Optional[int]
