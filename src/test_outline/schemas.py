from sqlite3 import Timestamp, Date
from typing import Optional
from pydantic import BaseModel, Field
from account.schemas import AccountGet


class OutlineGet(BaseModel):
    key_id: int
    name: str
    # password: str
    port: int
    method: str
    access_url: str
    used_bytes: Optional[int]
    data_limit: Optional[int]


class OutlineCreate(BaseModel):
    name: str


class OutlineUpdate(BaseModel):
    # key_id: int
    name: str
    # password: str
    # port: int
    # method: str
    # access_url: str
    # used_bytes: int
    # data_limit: int
