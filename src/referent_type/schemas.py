from typing import Optional
from pydantic import BaseModel, Field


class ReferentTypeGet(BaseModel):
    id: int
    name: str


class ReferentTypeCreate(BaseModel):
    id: int
    name: str = Field(..., title="referent_type")


class ReferentTypeUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]
