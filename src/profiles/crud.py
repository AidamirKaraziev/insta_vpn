from datetime import datetime
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import select, extract, func
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import crud_account
from config import MAX_PROFILE_TO_ACCOUNT
from core.base_crud import CRUDBase
from outline_key.crud import crud_outline_key
from profiles.models import Profile
from profiles.schemas import ProfileCreate, ProfileUpdate


class CrudProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    obj_name = "Profile"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}
    not_found_by_key_id_server_id = {"num": 404, "message": f"Not found a {obj_name} with this key_id and server_id"}
    cannot_delete_an_active_profile = {"num": 404, "message": f"Cannot delete an active {obj_name}"}
    too_many_profiles = {"num": 404, "message": f"Too many {obj_name}s"}

    async def get_profile_by_id(self, *, db: AsyncSession, id: UUID4):
        """Получение профиля по UUID4, если такого нет то вывод ошибки"""
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_profiles_by_account_id(self, *, db: AsyncSession, id: int):
        """Получение списка профилей по account_id, если их нет -> []"""
        account, code, indexes = await crud_account.get_account_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        query = select(self.model).where(self.model.account_id == id)
        response = await db.execute(query)
        obj = response.scalars().all()
        return obj, 0, None

    async def get_all_profiles(self, *, db: AsyncSession, skip: int, limit: int):
        """Список всех профилей, если их нет -> []"""
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def get_name_for_profile(self, *, db: AsyncSession, account_id: int):
        """
            Присваивает имя профиля для фронта. Номеруется от меньшего к большему.
            Проверяет максимальное количество профилей для одного аккаунта
            Пример: Профиль 1.
        """
        profiles, code, indexes = await self.get_profiles_by_account_id(db=db, id=account_id)
        if code != 0:
            return None, code, None
        if int(len(profiles)) > int(MAX_PROFILE_TO_ACCOUNT):
            return None, self.too_many_profiles, None
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

    # TODO check
    async def add_profile(self, *, db: AsyncSession, account_id: int):
        """Создание профиля с нужными полями, который по дефолту не активен:
            id: UUID4
            name: str
            account_id: int
            is_active: Optional[bool] = False"""
        uuid_value = uuid4()
        account, code, indexes = await crud_account.get_account_by_id(db=db, id=account_id)
        if code != 0:
            return None, code, None
        # получение имени для профиля
        name, code, indexes = await self.get_name_for_profile(db=db, account_id=account_id)
        if code != 0:
            return None, code, None
        new_data = ProfileCreate(id=uuid_value, account_id=account_id, name=name)
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def update_profile(self, *, db: AsyncSession, update_data: ProfileUpdate, id: UUID4):
        """Обновление данных в профиле:
            dynamic_key: Optional[str]
            shadowsocks_key_id: Optional[int]
            date_end: Optional[Timestamp]
            used_bytes: Optional[int]
            is_active: Optional[bool]"""
        profile, code, indexes = await self.get_profile_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        objects = await super().update(db_session=db, obj_current=profile, obj_new=update_data)
        return objects, 0, None

    # TODO test
    async def activate_profile(self, *, db: AsyncSession, activate_data: ProfileUpdate, id: UUID4):
        """Активирует профиль, указывается дата окончания и is_active: True,
         подбирается свободный outline_key"""
        profile, code, indexes = await self.get_profile_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        outline_key, code, indexes = await crud_outline_key.get_good_key(db=db)
        if code != 0:
            return None, code, None
        activate_data.is_active = True
        activate_data.outline_key_id = outline_key.id
        objects = await super().update(db_session=db, obj_current=profile, obj_new=activate_data)
        return objects, 0, None

    # TODO test
    async def deactivate_profile(self, *, db: AsyncSession, id: UUID4):
        """Деактивирует профиль: is_active -> False, outline_key_id -> None"""
        profile, code, indexes = await self.get_profile_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        deactivate_data = ProfileUpdate(is_active=False, outline_key_id=None)
        objects = await super().update(db_session=db, obj_current=profile, obj_new=deactivate_data)
        return objects, 0, None

    async def replacement_outline_key_for_profile(self, *, db: AsyncSession, profile_id: UUID4):
        """Замена outline_key_id в профиле. Выбирается самый первый свободный ключ"""
        profile, code, indexes = await self.get_profile_by_id(db=db, id=profile_id)
        if code != 0:
            return None, code, None
        outline_key, code, indexes = await crud_outline_key.get_replacement_key(
            db=db, outline_key_id=profile.outline_key_id)
        if code != 0:
            return None, code, None
        update_data = ProfileUpdate(outline_key_id=outline_key.id)
        profile, code, indexes = await self.update_profile(db=db, id=profile_id, update_data=update_data)
        if code != 0:
            return None, code, None
        return profile, 0, None

    async def get_profiles_by_date_end(self, *, db: AsyncSession, your_date: datetime):
        """Дает список активных профилей, где date_end < your_date"""
        query = select(self.model).where(self.model.date_end < your_date, self.model.is_active == True)
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

    async def delete_profile(self, *, db: AsyncSession, id: UUID4):
        """Удаление профиля с проверкой на активность. Нельзя удалить оплаченный профиль"""
        obj, code, indexes = await self.get_profile_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        if obj.is_active:
            return None, self.cannot_delete_an_active_profile, None
        obj = await super().delete(db=db, id=id)
        return obj, 0, None


crud_profile = CrudProfile(Profile)
