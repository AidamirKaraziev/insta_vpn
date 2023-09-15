from typing import Optional
from pydantic import BaseModel, Field


class ServerGet(BaseModel):
    id: int
    name: Optional[str]
    api_url: str
    cert_sha256: str
    max_client: Optional[int]
    fact_client: Optional[int]
    address: Optional[str]
    port: Optional[str]
    is_active: Optional[bool]


class ServerCreate(BaseModel):
    id: int
    name: Optional[str]
    api_url: str
    cert_sha256: str
    max_client: Optional[int]
    fact_client: Optional[int]
    address: Optional[str]
    port: Optional[str]
    is_active: Optional[bool]


class ServerUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]
    api_url: Optional[str]
    cert_sha256: Optional[str]
    max_client: Optional[int]
    fact_client: Optional[int]
    address: Optional[str]
    port: Optional[str]
    is_active: Optional[bool]
