from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from old_code.promo.models import Promo
from old_code.promo.schemas import PromoUpdate, PromoCreate

from core.base_crud import CRUDBase


class CrudPromo(CRUDBase[Promo, PromoCreate, PromoUpdate]):

    async def get_promo_by_id(self, *, db: AsyncSession, promo_id: int):
        obj = await super().get(db=db, id=promo_id)
        if obj is None:
            return None, "Not found promo with this id", None
        return obj, 0, None

    async def get_all_promo(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def create_promo(self, *, db: AsyncSession, new_data: PromoCreate):
        # check name
        query = select(self.model).where(self.model.name == new_data.name)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, "А promo with that name already exists", None
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def update_promo(self, *, db: AsyncSession, update_data: PromoUpdate, promo_id: int):
        # check id
        query = select(self.model).where(self.model.id == promo_id)
        resp = await db.execute(query)
        this_obj = resp.scalar_one_or_none()
        if this_obj is None:
            return None, "Not found promo with this id", None  # not_found
        # check name
        if update_data.name is not None:
            query = select(self.model).where(self.model.name == update_data.name, self.model.id != promo_id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is not None:
                return None, "А promo with that name already exists", None
        objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
        return objects, 0, None


crud_promo = CrudPromo(Promo)
