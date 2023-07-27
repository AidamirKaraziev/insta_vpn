from typing import Optional
from pydantic import BaseModel, Field


class TariffGet(BaseModel):
    id: int
    name: str
    price: int
    period_day: int
    is_active: bool


class TariffCreate(BaseModel):
    name: str = Field(..., title="tariff")
    price: int
    period_day: int
    is_active: Optional[bool]


class TariffUpdate(BaseModel):
    name: Optional[str]
    is_active: Optional[bool]
    price: Optional[int]
    period_day: Optional[int]
    is_active: Optional[bool]
