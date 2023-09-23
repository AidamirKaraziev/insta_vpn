from sqlite3 import Date
from typing import Optional

from fastapi_users import schemas

# from old_code.role.schemas import RoleGet


class UserRead(schemas.BaseUser[int]):
    id: Optional[int]
    name: Optional[str]
    photo: Optional[str]

    email: Optional[str]
    phone_number: Optional[str]
    registered_at: Optional[Date]
    # role_id: Optional[RoleGet]
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    name: str

    email: str
    phone_number: str

    password: str
    # role_id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]


# это нужно только для from main get_register_router
class UserReadOld(schemas.BaseUser[int]):
    id: Optional[int]
    name: Optional[str]
    photo: Optional[str]

    email: Optional[str]
    phone_number: Optional[str]
    registered_at: Optional[Date]
    # role_id: Optional[int]
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True
