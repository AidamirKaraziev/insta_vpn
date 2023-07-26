from typing import Optional
from pydantic import BaseModel, Field


class PromoGet(BaseModel):
    id: int
    name: str
    is_active: bool


# формальность
class PromoCreate(BaseModel):
    name: str = Field(..., title="Должность")
    is_active = bool


# формальность
class PromoUpdate(BaseModel):
    name: str = Field(..., title="Должность")
    is_active = bool


