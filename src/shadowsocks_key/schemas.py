from typing import Optional, Any
from pydantic import BaseModel, Field


class ShadowsocksKeyGet(BaseModel):
    id: int
    server_id: int

    key_id: int
    name: Optional[str]
    port: Optional[int]
    method: Optional[str]
    access_url: Optional[str]
    used_bytes: Optional[int]
    data_limit: Optional[int]
    password: Optional[str]

    is_active: Optional[bool]


class ShadowsocksKeyCreate(BaseModel):
    server_id: int

    key_id: int
    name: Optional[str]
    port: Optional[int]
    method: Optional[str]
    access_url: Optional[str]
    used_bytes: Optional[int]
    data_limit: Optional[int]
    password: Optional[str]

    is_active: Optional[bool]


class ShadowsocksKeyUpdate(BaseModel):
    # server_id: Optional[int]
    #
    # key_id: Optional[int]
    # name: Optional[str]
    # port: Optional[int]
    # method: Optional[str]
    # access_url: Optional[str]
    # used_bytes: Optional[int]
    # data_limit: Optional[int]
    # password: Optional[str]

    is_active: Optional[bool]
