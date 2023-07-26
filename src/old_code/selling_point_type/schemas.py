from typing import Optional
from pydantic import BaseModel


class SellingPointTypeGet(BaseModel):
    id: Optional[int]
    name: Optional[str]
    is_active: Optional[bool]


class SellingPointTypeCreate(BaseModel):
    name: str
    is_active: Optional[bool] = True


class SellingPointTypeUpdate(BaseModel):
    name: Optional[str]
    is_active: Optional[bool]

