from datetime import datetime
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import select, extract, func
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import crud_account
from config import OUTLINE_USERS_GATEWAY, CONN_NAME
from core.base_crud import CRUDBase
from profiles.models import Profile
from profiles.schemas import ProfileCreate, ProfileUpdate

from static_key.crud import crud_static_key


async def gen_outline_dynamic_link(profile_id: UUID4):
    return f"{OUTLINE_USERS_GATEWAY}/conf/{profile_id}#{CONN_NAME}"


class CrudProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    obj_name = "Profile"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}
    not_found_by_key_id_server_id = {"num": 404, "message": f"Not found a {obj_name} with this key_id and server_id"}
    not_found_by_server_id = {"num": 404, "message": f"Not found a {obj_name + 's'} with this server_id"}

    async def get_profile_by_id(self, *, db: AsyncSession, id: UUID4):
        obj = await super().get_by_uuid(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_profiles_by_account_id(self, *, db: AsyncSession, id: int):
        account, code, indexes = await crud_account.get_account_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        query = select(self.model).where(self.model.account_id == id)
        response = await db.execute(query)
        obj = response.scalars().all()
        return obj, 0, None

    async def get_all_profiles(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def add_profile(self, *, db: AsyncSession, account_id: int, name: str):
        uuid_value = uuid4()
        obj, code, indexes = await crud_account.get_account_by_id(db=db, id=account_id)
        if code != 0:
            return None, code, None
        new_data = ProfileCreate(id=uuid_value, account_id=account_id, name=name)
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def update_profile(self, *, db: AsyncSession, update_data: ProfileUpdate, id: UUID4):
        profile, code, indexes = await self.get_profile_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        objects = await super().update(db_session=db, obj_current=profile, obj_new=update_data)
        return objects, 0, None

    async def activate_profile(self, *, db: AsyncSession, activate_data: ProfileUpdate, id: UUID4):
        # check id
        profile, code, indexes = await self.get_profile_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        dynamic_key = await gen_outline_dynamic_link(profile_id=id)
        static_key, code, indexes = await crud_static_key.get_good_key(db=db)
        if code != 0:
            return None, code, None
        activate_data.is_active = True
        activate_data.dynamic_key = dynamic_key
        activate_data.static_key_id = static_key.id

        objects = await super().update(db_session=db, obj_current=profile, obj_new=activate_data)
        return objects, 0, None

    async def deactivate_profile(self, *, db: AsyncSession, id: UUID4):
        """Деактивирует профиль: is_active -> False, static_key_id -> None"""
        # check id
        profile, code, indexes = await self.get_profile_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        deactivate_data = ProfileUpdate(is_active=False, static_key_id=None)
        objects = await super().update(db_session=db, obj_current=profile, obj_new=deactivate_data)
        return objects, 0, None

    async def get_profile_by_key_id_server_id(self, *, db: AsyncSession, key_id: int, server_id: int):
        query = select(self.model).where(self.model.key_id == key_id, self.model.server_id == server_id)
        response = await db.execute(query)
        res = response.scalar_one_or_none()
        if res is None:
            return None, self.not_found_by_key_id_server_id, {"key_id": key_id, "server_id": server_id}
        return res, 0, None

    async def get_name_for_profile(self, *, db: AsyncSession, account_id: int):
        profiles, code, indexes = await self.get_profiles_by_account_id(db=db, id=account_id)
        if code != 0:
            return None, code, None
        num = 1
        name_list = []
        for profile in profiles:
            name_list.append(profile.name)
            if profile.name == f"Профиль {num}":
                num += 1
        for num in range(1, len(name_list)+2):
            if f"Профиль {num}" not in name_list:
                return f"Профиль {num}", 0, None
        return f"Профиль {num}", 0, None

    async def replacement_key(self, *, db: AsyncSession, profile_id: UUID4):
        profile, code, indexes = await self.get_profile_by_id(db=db, id=profile_id)
        if code != 0:
            return None, code, None
        static_key, code, indexes = await crud_static_key.get_replacement_key(
            db=db, static_key_id=profile.static_key_id)
        if code != 0:
            return None, code, None
        # update
        update_data = ProfileUpdate(static_key_id=static_key.id)
        profile, code, indexes = await self.update_profile(db=db, id=profile_id, update_data=update_data)
        if code != 0:
            return None, code, None
        return profile, 0, None

    async def get_profiles_by_date_end(self, *, db: AsyncSession, date_of_disconnection: datetime):
        """Дает список активных профилей у которых истек срок действия"""
        query = select(self.model).where(self.model.date_end < date_of_disconnection, self.model.is_active == True)
        response = await db.execute(query)
        obj = response.scalars().all()
        return obj, 0, None

    async def get_active_paid_profiles_per_month_in_year(self, *, db: AsyncSession, year_value: int):
        """Получить количество активных платных профилей для каждого месяца в указанном году."""
        query = (
            select(
                extract('month', self.model.date_end).label('month'),
                func.count().label('active_count')
            )
            .where(
                self.model.is_active == True,
                extract('year', self.model.date_end) == year_value
            )
            .group_by(extract('month', self.model.date_end))
            .order_by(extract('month', self.model.date_end))
        )
        response = await db.execute(query)
        results = response.all()
        return results, 0, None


crud_profile = CrudProfile(Profile)
