from sqlite3 import Timestamp, Date
from typing import Optional
from pydantic import BaseModel


class AccountGet(BaseModel):
    id: int
    name: Optional[str]
    number: Optional[str]
    created_at: Optional[Date]


class AccountCreate(BaseModel):
    id: int
    name: Optional[str]
    number: Optional[str]


class AccountUpdate(BaseModel):
    name: Optional[str]
    number: Optional[str]
