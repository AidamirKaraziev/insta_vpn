from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import select, extract, func
from sqlalchemy.ext.asyncio import AsyncSession


from config import OUTLINE_USERS_GATEWAY, CONN_NAME, MAX_PROFILE_TO_ACCOUNT, BASE_REFERRAL_LINK
from core.base_crud import CRUDBase


from referent.models import Referent
from referent.schemas import ReferentUpdate, ReferentCreate


# TODO


async def gen_referral_link(referent_id: UUID4):
    return f"{BASE_REFERRAL_LINK}{referent_id}"


class CrudReferent(CRUDBase[Referent, ReferentCreate, ReferentUpdate]):
    obj_name = "Referent"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}
    # not_found_by_key_id_server_id = {"num": 404, "message": f"Not found a {obj_name} with this key_id and server_id"}
    # cannot_delete_an_active_profile = {"num": 404, "message": f"Cannot delete an active {obj_name}"}
    # too_many_profiles = {"num": 404, "message": f"Too many {obj_name}s"}

    async def get_all_referents(self, *, db: AsyncSession, skip: int, limit: int):
        """Список всех референтов, если их нет -> []"""
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def get_referent_by_id(self, *, db: AsyncSession, id: UUID4):
        """Получение референта по UUID4, если такого нет то вывод ошибки"""
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def add_referent_for_client(self, *, db: AsyncSession, telegram_id: Optional[int]):
        """Создание референта с нужными полями, который по дефолту:
            id: UUID4
            telegram_id: Optional[int]
            description: Optional[str]
            referral_link: Optional[str]
            password: Optional[str]"""
        uuid_value = uuid4()
        referral_link = await gen_referral_link(referent_id=uuid_value)  # эта пизда выделена желтыx
        # TODO hex password
        password = []
        create_data = ReferentCreate(id=uuid_value, telegram_id=telegram_id,
                                     referral_link=referral_link, password=password)
        objects = await super().create(db_session=db, obj_in=create_data)
        return objects, 0, None

    async def add_referent_for_blogger(self, *, db: AsyncSession, description: Optional[str]):
        """Создание референта с нужными полями, который по дефолту:
            id: UUID4
            telegram_id: Optional[int]
            description: Optional[str]
            referral_link: Optional[str]
            password: Optional[str]"""
        uuid_value = uuid4()
        referral_link = await gen_referral_link(referent_id=uuid_value)  # эта пизда выделена желтыx

        # TODO hex password
        password = "hellow"
        create_data = ReferentCreate(id=uuid_value, description=description,
                                     referral_link=referral_link, password=password)
        objects = await super().create(db_session=db, obj_in=create_data)
        return objects, 0, None
    # TODO update


crud_referent = CrudReferent(Referent)

#
# async def get_profiles_by_account_id(self, *, db: AsyncSession, id: int):
#     """Получение списка профилей по account_id, если их нет -> []"""
#     account, code, indexes = await crud_account.get_account_by_id(db=db, id=id)
#     if code != 0:
#         return None, code, None
#     query = select(self.model).where(self.model.account_id == id)
#     response = await db.execute(query)
#     obj = response.scalars().all()
#     return obj, 0, None
#
#

#
#
# async def update_profile(self, *, db: AsyncSession, update_data: ProfileUpdate, id: UUID4):
#     """Обновление данных в профиле:
#         dynamic_key: Optional[str]
#         static_key_id: Optional[int]
#         date_end: Optional[Timestamp]
#         used_bytes: Optional[int]
#         is_active: Optional[bool]"""
#     profile, code, indexes = await self.get_profile_by_id(db=db, id=id)
#     if code != 0:
#         return None, code, None
#     objects = await super().update(db_session=db, obj_current=profile, obj_new=update_data)
#     return objects, 0, None
#
#
# async def activate_profile(self, *, db: AsyncSession, activate_data: ProfileUpdate, id: UUID4):
#     """Активирует профиль, указывается дата окончания и is_active: True,
#      подбирается свободный static_key"""
#     profile, code, indexes = await self.get_profile_by_id(db=db, id=id)
#     if code != 0:
#         return None, code, None
#     static_key, code, indexes = await crud_static_key.get_good_key(db=db)
#     if code != 0:
#         return None, code, None
#     activate_data.is_active = True
#     activate_data.static_key_id = static_key.id
#     objects = await super().update(db_session=db, obj_current=profile, obj_new=activate_data)
#     return objects, 0, None
#
#
# async def deactivate_profile(self, *, db: AsyncSession, id: UUID4):
#     """Деактивирует профиль: is_active -> False, static_key_id -> None"""
#     profile, code, indexes = await self.get_profile_by_id(db=db, id=id)
#     if code != 0:
#         return None, code, None
#     deactivate_data = ProfileUpdate(is_active=False, static_key_id=None)
#     objects = await super().update(db_session=db, obj_current=profile, obj_new=deactivate_data)
#     return objects, 0, None
#
#
# async def get_name_for_profile(self, *, db: AsyncSession, account_id: int):
#     """
#         Присваивает имя профиля для фронта. Номеруется от меньшего к большему.
#         Проверяет максимальное количество профилей для одного аккаунта
#         Пример: Профиль 1.
#     """
#     profiles, code, indexes = await self.get_profiles_by_account_id(db=db, id=account_id)
#     if code != 0:
#         return None, code, None
#     if int(len(profiles)) > int(MAX_PROFILE_TO_ACCOUNT):
#         return None, self.too_many_profiles, None
#     num = 1
#     name_list = []
#     for profile in profiles:
#         name_list.append(profile.name)
#         if profile.name == f"Профиль {num}":
#             num += 1
#     for num in range(1, len(name_list) + 2):
#         if f"Профиль {num}" not in name_list:
#             return f"Профиль {num}", 0, None
#     return f"Профиль {num}", 0, None
#
#
# async def replacement_key(self, *, db: AsyncSession, profile_id: UUID4):
#     """Замена static_key_id в профиле. Выбирается самый первый свободный ключ"""
#     profile, code, indexes = await self.get_profile_by_id(db=db, id=profile_id)
#     if code != 0:
#         return None, code, None
#     static_key, code, indexes = await crud_static_key.get_replacement_key(
#         db=db, static_key_id=profile.static_key_id)
#     if code != 0:
#         return None, code, None
#     # update
#     update_data = ProfileUpdate(static_key_id=static_key.id)
#     profile, code, indexes = await self.update_profile(db=db, id=profile_id, update_data=update_data)
#     if code != 0:
#         return None, code, None
#     return profile, 0, None
#
#
# async def get_profiles_by_date_end(self, *, db: AsyncSession, your_date: datetime):
#     """Дает список активных профилей, где date_end < your_date"""
#     query = select(self.model).where(self.model.date_end < your_date, self.model.is_active == True)
#     response = await db.execute(query)
#     obj = response.scalars().all()
#     return obj, 0, None
#
#
# async def get_active_paid_profiles_per_month_in_year(self, *, db: AsyncSession, year_value: int):
#     """Получить количество активных платных профилей для каждого месяца в указанном году."""
#     query = (
#         select(
#             extract('month', self.model.date_end).label('month'),
#             func.count().label('active_count')
#         )
#         .where(
#             self.model.is_active == True,
#             extract('year', self.model.date_end) == year_value
#         )
#         .group_by(extract('month', self.model.date_end))
#         .order_by(extract('month', self.model.date_end))
#     )
#     response = await db.execute(query)
#     results = response.all()
#     return results, 0, None
#
#
# async def delete_profile(self, *, db: AsyncSession, id: UUID4):
#     """Удаление профиля с проверкой на активность. Нельзя удалить оплаченный профиль"""
#     obj, code, indexes = await self.get_profile_by_id(db=db, id=id)
#     if code != 0:
#         return None, code, None
#     if obj.is_active:
#         return None, self.cannot_delete_an_active_profile, None
#     obj = await super().delete(db=db, id=id)
#     return obj, 0, None
