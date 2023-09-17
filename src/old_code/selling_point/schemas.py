from typing import Optional
from pydantic import BaseModel

from auth.schemas import UserRead
from old_code.selling_point_type.schemas import SellingPointTypeGet


class SellingPointGet(BaseModel):
    id: int
    name: str
    photo: Optional[str]
    selling_point_type_id: Optional[SellingPointTypeGet]
    opening_hours: Optional[str]

    address: str

    client_id: Optional[UserRead]
    is_active: Optional[bool]


class SellingPointCreate(BaseModel):
    name: str
    selling_point_type_id: Optional[int]

    address: str
    opening_hours: Optional[str]

    client_id: Optional[int]
    is_active: Optional[bool] = True


class SellingPointUpdate(BaseModel):

    name: Optional[str]
    selling_point_type_id: Optional[int]
    address: Optional[str]
    opening_hours: Optional[str]
    is_active: Optional[bool]
      