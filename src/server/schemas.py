from typing import Optional
from pydantic import BaseModel, Field

from config import OUTLINE_VPN_TYPE


class ServerGet(BaseModel):
    id: int
    vpn_type_id: Optional[int]
    name: Optional[str]
    address: Optional[str]
    port: Optional[str]

    api_url: Optional[str]
    cert_sha256: Optional[str]

    marzban_login: Optional[str]
    marzban_pass: Optional[str]

    max_client: Optional[int]
    fact_client: Optional[int]

    is_active: Optional[bool]


class ServerCreate(BaseModel):
    pass


class OutlineServerCreate(ServerCreate):
    id: int
    vpn_type_id: int = OUTLINE_VPN_TYPE.id
    name: str
    address: str
    port: str

    api_url: str
    cert_sha256: str

    max_client: int
    is_active: Optional[bool] = True


class VlessServerCreate(BaseModel):
    id: int
    vpn_type_id: int
    name: str
    address: str
    port: str

    marzban_login: str
    marzban_pass: str

    max_client: int
    is_active: Optional[bool]


class ServerUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]

    fact_client: Optional[int]
    is_active: Optional[bool]


class MaxClientServerUpdate(BaseModel):
    max_client: Optional[int]
