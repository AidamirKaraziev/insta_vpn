from sqlite3 import Timestamp, Date
from typing import Optional
from pydantic import BaseModel, Field
from account.schemas import AccountGet

from server.schemas import ServerGet


class ProfileGet(BaseModel):
    id: int
    account_id: AccountGet
    server_id: ServerGet
    peer_name: str
    date_end: Optional[Date]
    created_at: Optional[Date]
    is_active: Optional[bool]


class ProfileCreate(BaseModel):
    account_id: int
    server_id: int
    peer_name: str
    is_active: Optional[bool]


class ProfileUpdate(BaseModel):
    date_end: Optional[Date]
    is_active: Optional[bool]
