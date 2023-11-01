from sqlite3 import Timestamp
from typing import Optional
from pydantic import BaseModel, UUID4


class ProfileGet(BaseModel):
    id: UUID4
    name: Optional[str]
    account_id: int

    dynamic_key: Optional[str]
    shadowsocks_key_id: Optional[int]
    vless_key_id: Optional[int]

    date_end: Optional[str]
    used_bytes: Optional[int]
    vpn_type_id: Optional[int]
    is_active: Optional[bool]


class ProfileCreate(BaseModel):
    id: UUID4
    name: str
    account_id: int

    dynamic_key: Optional[str]
    shadowsocks_key_id: Optional[int]
    vless_key_id: Optional[int]

    date_end: Optional[str]
    vpn_type_id: Optional[int]
    is_active: Optional[bool]


class ProfileUpdate(BaseModel):
    dynamic_key: Optional[str]
    shadowsocks_key_id: Optional[int]
    vless_key_id: Optional[int]

    date_end: Optional[str]
    used_bytes: Optional[int]
    vpn_type_id: Optional[int]
    is_active: Optional[bool]
