from typing import Optional
from pydantic import BaseModel


class OutlineKeyGet(BaseModel):
    id: int
    server_id: int

    key_id: int
    name: Optional[str]
    port: Optional[int]
    method: Optional[str]
    access_url: Optional[str]
    used_bytes: Optional[int]
    data_limit: Optional[int]
    password: Optional[str]

    is_active: Optional[bool]


class OutlineKeyCreate(BaseModel):
    server_id: int

    key_id: int
    name: Optional[str]
    port: Optional[int]
    method: Optional[str]
    access_url: Optional[str]
    used_bytes: Optional[int]
    data_limit: Optional[int]
    password: Optional[str]

    is_active: Optional[bool]


class OutlineKeyUpdate(BaseModel):
    is_active: Optional[bool]
