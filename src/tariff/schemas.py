from typing import Optional
from pydantic import BaseModel, Field


class TariffGet(BaseModel):
    id: int
    name: str
    price: int
    period_days: int
    photo_url: Optional[str]
    is_active: bool


class TariffCreate(BaseModel):
    id: Optional[int]
    name: str = Field(..., title="tariff")
    price: int
    period_days: int
    photo_url: Optional[str]
    is_active: Optional[bool]


class TariffUpdate(BaseModel):
    name: Optional[str]
    is_active: Optional[bool]
    price: Optional[int]
    period_days: Optional[int]
    photo_url: Optional[str]
    is_active: Optional[bool]
