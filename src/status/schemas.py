from typing import Optional
from pydantic import BaseModel, Field


class StatusGet(BaseModel):
    id: int
    name: str


class StatusCreate(BaseModel):
    id: int
    name: str = Field(..., title="status")


class StatusUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]
