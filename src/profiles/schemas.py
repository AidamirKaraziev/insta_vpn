from typing import Optional
from pydantic import BaseModel, UUID4
from sqlite3 import Timestamp


class ProfileGet(BaseModel):
    id: UUID4
    name: Optional[str]
    account_id: int

    dynamic_key: Optional[str]
    outline_key_id: Optional[int]

    date_end: Optional[Timestamp]
    used_bytes: Optional[int]
    is_active: Optional[bool]


class ProfileCreate(BaseModel):
    id: UUID4
    name: str
    account_id: int

    is_active: Optional[bool] = False


class ProfileUpdate(BaseModel):
    outline_key_id: Optional[int]

    date_end: Optional[Timestamp]
    used_bytes: Optional[int]
    is_active: Optional[bool]
