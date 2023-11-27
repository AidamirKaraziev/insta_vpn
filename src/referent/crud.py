from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import select, extract, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_crud import CRUDBase


from referent.models import Referent
from referent.schemas import ReferentUpdate, ReferentCreate


class CrudReferent(CRUDBase[Referent, ReferentCreate, ReferentUpdate]):
    obj_name = "Референт"
    not_found_id = {"num": 404, "message": f"Не нашли {obj_name}а с таким id"}
    telegram_id_is_exist = {"num": 403, "message": f"{obj_name} с таким telegram_id уже есть"}

    async def get_all_referents(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def get_referent_by_id(self, *, db: AsyncSession, id: UUID4):
        """
            Проверяем id, если такого нет - возвращает ошибку.
            Возвращаем по id.
        """
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_by_telegram_id(self, *, db: AsyncSession, telegram_id: int):
        """Возвращает список референтов, по телеграм id"""
        res = select(self.model).where(self.model.telegram_id == telegram_id)
        response = await db.execute(res)
        objs = response.scalars().all()
        return objs, 0, None

    async def create_native_referent(self, *, db: AsyncSession, new_data: ReferentCreate):
        """
            telegram_id: int

            gift_days: Optional[int] = BASE_REFERENT_GIFT_DAYS
            partner_id: Optional[int] = BASE_PARTNER
            referent_type_id: Optional[int]

            description: Optional[str]
            password: Optional[str]
        """
        # TODO Возможно вынести в отдельную функцию
        res = select(self.model).where(self.model.telegram_id == new_data.telegram_id, self.model.referent_type_id == 1)
        response = await db.execute(res)
        referent = response.scalar_one_or_none()
        if referent is not None:
            return referent, 0, None
        else:
            new_data.referent_type_id = 1
            new_data.partner_id = 1
            new_data.description = None
            new_data.password = None

            objects = await super().create(db_session=db, obj_in=new_data)
            return objects, 0, None


crud_referent = CrudReferent(Referent)
#
# async def update_account(self, *, db: AsyncSession, update_data: AccountUpdate, id: int):
#     # check id
#     query = select(self.model).where(self.model.id == id)
#     resp = await db.execute(query)
#     this_obj = resp.scalar_one_or_none()
#     if this_obj is None:
#         return None, self.not_found_id, None
#
#     objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
#     return objects, 0, None
#
# async def get_accounts_without_profile(self, db: AsyncSession):
#     """Возвращает список аккаунтов, у которых нет профиля"""
#     res = select(self.model).select_from(self.model).where(
#         ~exists().where(self.model.id == Profile.account_id))
#     response = await db.execute(res)
#     objs = response.scalars().all()
#     return objs, 0, None