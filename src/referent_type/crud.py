from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_crud import CRUDBase
from referent_type.models import ReferentType
from referent_type.schemas import ReferentTypeCreate, ReferentTypeUpdate


class CrudReferentType(CRUDBase[ReferentType, ReferentTypeCreate, ReferentTypeUpdate]):
    obj_name = "Тип референта"
    not_found_id = {"num": 404, "message": f"{obj_name}: нет с таким id."}
    name_is_exist = {"num": 403, "message": f"{obj_name}: с таким именем уже есть."}
    id_is_exist = {"num": 403, "message": f"{obj_name}: с таким id уже есть"}

    async def get_all_referent_types(self, *, db: AsyncSession, skip: int, limit: int):
        """
            Выводим список всех статусов.
        """
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def get_referent_type_by_id(self, *, db: AsyncSession, id: int):
        """
            Проверяем id, если такого нет - возвращает ошибку.
            Возвращаем по id.
        """
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def add_referent_type(self, *, db: AsyncSession, new_data: ReferentTypeCreate):
        """
            Проверяем id, если такой есть - возвращает ошибку.
            Проверяем name, если такой есть - возвращает ошибку.
        """
        # check id
        obj, code, indexes = await self.get_referent_type_by_id(db=db, id=new_data.id)
        if obj:
            return None, self.id_is_exist, None
        # check name
        query = select(self.model).where(self.model.name == new_data.name)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, self.name_is_exist, None
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def update_referent_type(self, *, db: AsyncSession, update_data: ReferentTypeUpdate, id: int):
        """
            Проверяем id, если такого нет - возвращает ошибку.
            Проверяем update_data.id, если такой есть не у изменяемого объекта - возвращает ошибку.
            Проверяем name, если такой есть - возвращает ошибку.
        """
        this_obj, code, indexes = await self.get_referent_type_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        if update_data.id is not None and this_obj.id != update_data.id:
            obj, code, indexes = await self.get_referent_type_by_id(db=db, id=update_data.id)
            if obj is not None:
                return None, self.id_is_exist, None
        # check name
        if update_data.name is not None:
            query = select(self.model).where(self.model.name == update_data.name, self.model.id != id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is not None:
                return None, self.name_is_exist, None
        objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
        return objects, 0, None


crud_referent_type = CrudReferentType(ReferentType)
