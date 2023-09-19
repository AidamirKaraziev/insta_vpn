from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import crud_account
from config import FREE_TRAFFIC, LIMIT_PROFILES
from core.base_crud import CRUDBase
from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from profiles.models import Profile
from profiles.schemas import ProfileCreate, ProfileUpdate, ProfileActivate
from server.crud import crud_server


class CrudProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    obj_name = "Profile"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}

    async def get_profile_by_id(self, *, db: AsyncSession, id: int):
        obj = await super().get(db=db, id=id)
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

    async def add_profile(self, *, db: AsyncSession, new_data: ProfileCreate):
        obj, code, indexes = await crud_account.get_account_by_id(db=db, id=new_data.account_id)
        if code != 0:
            return None, code, None
        obj, code, indexes = await crud_server.get_server_by_id(db=db, id=new_data.server_id)
        if code != 0:
            return None, code, None
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def update_profile(self, *, db: AsyncSession, update_data: ProfileUpdate, id: int):
        # check id
        query = select(self.model).where(self.model.id == id)
        resp = await db.execute(query)
        this_obj = resp.scalar_one_or_none()
        if this_obj is None:
            return None, self.not_found_id, None
        objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
        return objects, 0, None

    async def delete_profile(self, *, db: AsyncSession, id: int):
        obj, code, indexes = await self.get_profile_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        obj = await super().delete(db=db, id=id)
        return obj, 0, None

    async def activate_profile(self, *, db: AsyncSession, activate_data: ProfileActivate, id: int):
        # check id
        profile, code, indexes = await self.get_profile_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        objects = await super().update(db_session=db, obj_current=profile, obj_new=activate_data)
        return objects, 0, None

    async def activate_paid_profiles(self, db: AsyncSession, skip: int = 0):
        # get all profiles
        profiles, code, indexes = await self.get_all_profiles(db=db, skip=skip, limit=LIMIT_PROFILES)
        for profile in profiles:
            if profile.date_end > datetime.date(datetime.now()):
                # add data_limit
                server, code, indexes = await crud_server.get_server_by_id(db=db, id=profile.server_id)
                try:
                    client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
                    client.delete_data_limit(key_id=profile.key_id)
                except Exception as ex:
                    return None, self.outline_error(ex=ex), None
                update_data = ProfileUpdate(data_limit=None, is_active=True)
                obj, code, indexes = await self.update_profile(db=db, update_data=update_data, id=profile.id)
        return profiles, code, indexes

    async def get_profile_by_key_id_server_id(self, *, db: AsyncSession, key_id: int, server_id: int):
        query = select(self.model).where(self.model.key_id == key_id, self.model.server_id == server_id)
        response = await db.execute(query)
        res = response.scalar_one_or_none()
        if res is None:
            return None, self.not_found_id, {"key_id": key_id, "server_id": server_id}
        return res, 0, None

    async def get_name_for_profile(self, *, db: AsyncSession, account_id: int):
        profiles, code, indexes = await self.get_profiles_by_account_id(db=db, id=account_id)
        if code != 0:
            return None, code, None
        num = 1
        for profile in profiles:
            if profile.name == f"Профиль {num}":
                num += 1
            return f"Профиль {num+1}", 0, None


crud_profile = CrudProfile(Profile)
