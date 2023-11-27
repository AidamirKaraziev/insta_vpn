from typing import Optional
from pydantic import BaseModel


class VlessKeyGet(BaseModel):
    id: int
    link: str
    server_ip: str
    is_active: Optional[bool]


class VlessKeyCreate(BaseModel):
    link: str
    server_ip: str
    is_active: Optional[bool]


class VlessKeyUpdate(BaseModel):
    is_active: Optional[bool]
