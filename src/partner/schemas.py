from typing import Optional
from pydantic import BaseModel, Field


class PartnerGet(BaseModel):
    id: int
    name: str


class PartnerCreate(BaseModel):
    id: int
    name: str = Field(..., title="partner")


class PartnerUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]
