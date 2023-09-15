from sqlite3 import Timestamp, Date
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import DateTime


class AccountGet(BaseModel):
    id: int
    name: Optional[str]
    number: Optional[str]
    created_at: Optional[Timestamp]


class AccountCreate(BaseModel):
    id: int
    name: Optional[str]
    number: Optional[str]


class AccountUpdate(BaseModel):
    name: Optional[str]
    number: Optional[str]
