from typing import Optional
from pydantic import BaseModel, Field


class PaymentGet(BaseModel):
    id: int
    name: str


class PaymentCreate(BaseModel):
    id: int
    name: str = Field(..., title="partner")


class PaymentUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]

