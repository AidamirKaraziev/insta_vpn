from sqlalchemy.ext.asyncio import AsyncSession

from old_code.auth.models import User
from old_code.auth.schemas import UserCreate, UserUpdate
from core.base_crud import CRUDBase


class CrudUser(CRUDBase[User, UserCreate, UserUpdate]):

    async def get_user_by_id(self, *, db: AsyncSession, user_id: int):
        obj = await super().get(db=db, id=user_id)
        if obj is None:
            return None, "Not found user with this id", None
        return obj, 0, None

    async def get_all_users(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None


crud_user = CrudUser(User)
