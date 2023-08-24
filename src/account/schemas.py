from sqlite3 import Timestamp, Date
from typing import Optional
from pydantic import BaseModel


class AccountGet(BaseModel):
    id: int
    name: Optional[str]
    number: Optional[str]
    telegram_id: int
    created_at: Optional[Date]
    time_zone: Optional[str]


class AccountCreate(BaseModel):
    name: Optional[str]
    number: Optional[str]
    telegram_id: int
    time_zone: Optional[str]


class AccountUpdate(BaseModel):
    name: Optional[str]
    number: Optional[str]
    time_zone: Optional[str]
