from sqlite3 import Timestamp, Date
from typing import Optional
from pydantic import BaseModel, Field


from account.schemas import AccountGet
from ip_address.schemas import IpAddressGet


class ProfileGet(BaseModel):
    id: int
    account_id: AccountGet
    ip_address_id: IpAddressGet
    peer_name: str
    date_end: Optional[int]
    created_at: Optional[int]
    is_active: Optional[bool]


class ProfileCreate(BaseModel):
    account_id: int
    ip_address_id: int
    peer_name: str
    is_active: Optional[bool]


class ProfileUpdate(BaseModel):
    date_end: Optional[Date]
    is_active: Optional[bool]
