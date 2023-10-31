from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from account.models import Account
from account.schemas import AccountCreate, AccountUpdate
from core.base_crud import CRUDBase


# TODO дополнить круд в соответствии с моделью и схемой
class CrudAccount(CRUDBase[Account, AccountCreate, AccountUpdate]):
    obj_name = "Account"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}
    telegram_id_is_exist = {"num": 403, "message": f"А {obj_name} with that telegram id already exists"}

    async def get_account_by_id(self, *, db: AsyncSession, id: int):
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_all_accounts(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def add_account(self, *, db: AsyncSession, new_data: AccountCreate):
        query = select(self.model).where(self.model.id == new_data.id)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, self.telegram_id_is_exist, None
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def update_account(self, *, db: AsyncSession, update_data: AccountUpdate, id: int):
        # check id
        query = select(self.model).where(self.model.id == id)
        resp = await db.execute(query)
        this_obj = resp.scalar_one_or_none()
        if this_obj is None:
            return None, self.not_found_id, None

        objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
        return objects, 0, None


crud_account = CrudAccount(Account)
