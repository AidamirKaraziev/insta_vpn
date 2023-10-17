from sqlite3 import Timestamp, Date
from typing import Optional, Any
from pydantic import BaseModel, Field


class ProfileGet(BaseModel):
    id: int
    name: str
    account_id: int

    dynamic_key: str
    static_key_id: Optional[int]

    date_end: Optional[str]
    used_bytes: Optional[int]
    is_active: Optional[bool]


class ProfileCreate(BaseModel):
    name: str
    account_id: int

    dynamic_key: str

    date_end: Optional[Timestamp]
    is_active: Optional[bool]


class ProfileUpdate(BaseModel):
    static_key_id: Optional[int]

    date_end: Optional[Timestamp]
    used_bytes: Optional[int]
    is_active: Optional[bool]


class ProfileActivate(BaseModel):
    static_key_id: Optional[int]
    date_end: Optional[Timestamp]
    is_active: Optional[bool] = True
