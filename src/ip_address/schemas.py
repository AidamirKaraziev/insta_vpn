from typing import Optional
from pydantic import BaseModel, Field


class IpAddressGet(BaseModel):
    id: int
    name: str
    is_active: bool


class IpAddressCreate(BaseModel):
    name: str = Field(..., title="ip address")
    is_active: Optional[bool]


class IpAddressUpdate(BaseModel):
    name: Optional[str] = Field(..., title="ip address")
    is_active: Optional[bool]
