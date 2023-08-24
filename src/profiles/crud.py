from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import crud_account
from core.base_crud import CRUDBase
from profiles.models import Profile
from profiles.schemas import ProfileCreate, ProfileUpdate
from server.crud import crud_server


class CrudProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    obj_name = "Profile"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}

    async def get_profile_by_id(self, *, db: AsyncSession, id: int):
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
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


crud_profile = CrudProfile(Profile)
