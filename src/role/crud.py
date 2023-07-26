from sqlalchemy.ext.asyncio import AsyncSession

from core.base_crud import CRUDBase
from role.models import Role
from role.schemas import RoleCreate, RoleUpdate


class CrudRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_role_by_id(self, *, db: AsyncSession, role_id: int):
        obj = await super().get(db=db, id=role_id)
        if obj is None:
            return None, "Not found role with this id", None
        return obj, 0, None

    async def get_all_role(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None


crud_role = CrudRole(Role)
