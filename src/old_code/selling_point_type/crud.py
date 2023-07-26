from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from old_code.selling_point_type.models import SellingPointType
from old_code.selling_point_type.schemas import SellingPointTypeCreate, SellingPointTypeUpdate

from core.base_crud import CRUDBase


class CrudSellingPointType(CRUDBase[SellingPointType, SellingPointTypeCreate, SellingPointTypeUpdate]):

    async def get_selling_point_type_by_id(self, *, db: AsyncSession, selling_point_type_id: int):
        selling_point_type = await self.get(db=db, id=selling_point_type_id)
        if selling_point_type is None:
            return None, "Not found selling point type with this id", None
        return selling_point_type, 0, None

    async def get_all_selling_point_types(self, *, db: AsyncSession, skip: int, limit: int):
        selling_point_types = await self.get_multi(db_session=db, skip=skip, limit=limit)
        return selling_point_types, 0, None

    async def create_selling_point_type(self, *, db: AsyncSession, new_data: SellingPointTypeCreate):
        # check name
        query = select(self.model).where(self.model.name == new_data.name)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, "А selling point type with that name already exists", None
        new_selling_point_type = await self.create(db_session=db, obj_in=new_data)
        return new_selling_point_type, 0, None

    async def update_selling_point_type(self,
                                        *,
                                        db: AsyncSession,
                                        update_data: SellingPointTypeUpdate,
                                        selling_point_type_id: int):
        # check by id
        query = select(self.model).where(self.model.id == selling_point_type_id)
        response = await db.execute(query)
        current_selling_point_type = response.scalar_one_or_none()
        if current_selling_point_type is None:
            return None, "Not found selling point type with this id", None
        # check name
        if update_data.name is not None:
            query = select(self.model).where(self.model.name == update_data.name, self.model.id != selling_point_type_id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is not None:
                return None, "А selling point type with that name already exists", None
        updated_selling_point_type = await self.update(db_session=db,
                                                       obj_current=current_selling_point_type,
                                                       obj_new=update_data)
        return updated_selling_point_type, 0, None


crud_selling_point_type = CrudSellingPointType(SellingPointType)
