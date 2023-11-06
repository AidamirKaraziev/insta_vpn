from typing import Optional
from pydantic import BaseModel, Field


class VpnTypeGet(BaseModel):
    id: int
    name: str


class VpnTypeCreate(BaseModel):
    id: int
    name: str = Field(..., title="vpn_type")


class VpnTypeUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]
