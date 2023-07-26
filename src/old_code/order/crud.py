from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from old_code.order.models import Order
from old_code.order.schemas import OrderCreate, OrderUpdate

from old_code.selling_point.models import SellingPoint
from old_code.order_status.models import Status
from core.base_crud import CRUDBase


class CrudOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):

    async def get_order_by_id(self, *, db: AsyncSession, order_id: int):
        obj = await self.get(db=db, id=order_id)
        if obj is None:
            return None, "Not found order with this id", None
        return obj, 0, None

    async def get_all_orders(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await self.get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def create_order(self, *, db: AsyncSession, new_data: OrderCreate):
        # check selling_point
        if new_data.selling_point_id is not None:
            query = select(SellingPoint).where(SellingPoint.id == new_data.selling_point_id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is None:
                return None, "Not found selling point with this id", None

        # check order_status
        query = select(Status).where(Status.id == new_data.status_id)
        response = await db.execute(query)
        if response.scalar_one_or_none() is None:
            return None, "Not found order_status with this id", None
        objects = await self.create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def update_order(self, *, db: AsyncSession, update_data: OrderUpdate, order_id: int):
        # check id
        query = select(self.model).where(self.model.id == order_id)
        response = await db.execute(query)
        current_obj = response.scalar_one_or_none()
        if current_obj is None:
            return None, "Not found order with this id", None
        objects = await self.update(db_session=db, obj_current=current_obj, obj_new=update_data)
        return objects, 0, None


crud_order = CrudOrder(Order)
