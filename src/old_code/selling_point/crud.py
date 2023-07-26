from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from old_code.selling_point.models import SellingPoint
from old_code.selling_point.schemas import SellingPointCreate, SellingPointUpdate

from core.base_crud import CRUDBase


class CrudSellingPoint(CRUDBase[SellingPoint, SellingPointCreate, SellingPointUpdate]):

    async def get_selling_point_by_id(self, *, db: AsyncSession, selling_point_id: int):
        selling_point = await self.get(db=db, id=selling_point_id)
        if selling_point is None:
            return None, "Not found selling point with this id", None
        return selling_point, 0, None

    async def get_all_selling_points(self, *, db: AsyncSession, skip: int, limit: int):
        selling_points = await self.get_multi(db_session=db, skip=skip, limit=limit)
        return selling_points, 0, None

    async def create_selling_point(self, *, db: AsyncSession, new_data: SellingPointCreate):
        # check name
        query = select(self.model).where(self.model.name == new_data.name)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, "А selling point with that name already exists", None
        new_selling_point = await self.create(db_session=db, obj_in=new_data)
        return new_selling_point, 0, None

    async def update_selling_point(self, *, db: AsyncSession, update_data: SellingPointUpdate, selling_point_id: int):
        # check id
        query = select(self.model).where(self.model.id == selling_point_id)
        response = await db.execute(query)
        current_selling_point = response.scalar_one_or_none()
        if current_selling_point is None:
            return None, "Not found selling point with this id", None
        # check name
        if update_data.name is not None:
            query = select(self.model).where(self.model.name == update_data.name, self.model.id != selling_point_id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is not None:
                return None, "А selling point with that name already exists", None
        updated_selling_point = await self.update(db_session=db, obj_current=current_selling_point, obj_new=update_data)
        return updated_selling_point, 0, None

    async def check_name(self, *, witch_name: str):
        if witch_name not in ["photo"]:
            return f"Incorrect witch photo name '{witch_name}'!"


crud_selling_point = CrudSellingPoint(SellingPoint)
