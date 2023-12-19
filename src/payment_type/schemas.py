from typing import Optional
from pydantic import BaseModel, Field


class PaymentTypeGet(BaseModel):
    id: int
    name: str


class PaymentTypeCreate(BaseModel):
    id: int
    name: str = Field(..., title="payment_type")


class PaymentTypeUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]
