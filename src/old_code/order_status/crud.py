from sqlalchemy.ext.asyncio import AsyncSession

from old_code.order_status.models import Status
from old_code.order_status.schemas import StatusCreate, StatusUpdate

from core.base_crud import CRUDBase


class CrudStatus(CRUDBase[Status, StatusCreate, StatusUpdate]):

    async def get_status_by_id(self, *, db: AsyncSession, status_id: int):
        obj = await self.get(db=db, id=status_id)
        if obj is None:
            return None, "Not found order_status with this id", None
        return obj, 0, None

    async def get_all_statuses(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await self.get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None


crud_status = CrudStatus(Status)
