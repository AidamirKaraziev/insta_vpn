from sqlite3 import Timestamp, Date
from typing import Optional, Any
from pydantic import BaseModel, Field


class ProfileGet(BaseModel):
    id: int
    account_id: int
    server_id: int

    key_id: int
    name: Optional[str]
    port: Optional[int]
    method: Optional[str]
    access_url: Optional[str]
    used_bytes: Optional[int]
    data_limit: Optional[int]

    date_end: Optional[str]
    is_active: Optional[bool]


class ProfileCreate(BaseModel):
    account_id: int
    server_id: int

    key_id: int
    name: Optional[str]
    port: Optional[int]
    method: Optional[str]
    access_url: Optional[str]
    used_bytes: Optional[int]
    data_limit: Optional[int]

    date_end: Optional[Timestamp]
    is_active: Optional[bool]


class ProfileUpdate(BaseModel):
    account_id: Optional[int]
    server_id: Optional[int]

    key_id: Optional[int]
    name: Optional[str]
    port: Optional[int]
    method: Optional[str]
    access_url: Optional[str]
    used_bytes: Optional[int]
    data_limit: Optional[int]

    date_end: Optional[Timestamp]
    is_active: Optional[bool]


class ProfileActivate(BaseModel):
    data_limit: int = None
    date_end: Optional[Timestamp]
    is_activate: Optional[bool] = True
