from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from old_code.dish.models import Dish
from old_code.dish.schemas import DishCreate, DishUpdate

from core.base_crud import CRUDBase
from old_code.promo.models import Promo


class CrudDish(CRUDBase[Dish, DishCreate, DishUpdate]):

    async def get_dish_by_id(self, *, db: AsyncSession, dish_id: int):
        obj = await self.get(db=db, id=dish_id)
        if obj is None:
            return None, "Not found dish with this id", None
        return obj, 0, None

    async def get_all_dishes(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await self.get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def create_dish(self, *, db: AsyncSession, new_data: DishCreate):
        # check name
        query = select(self.model).where(self.model.name == new_data.name)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, "А dish with that name already exists", None
        # check promo id
        if new_data.promo_id is not None:
            query = select(Promo).where(Promo.id == new_data.promo_id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is None:
                return None, "Not found promo with this id", None
        objects = await self.create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def update_dish(self, *, db: AsyncSession, update_data: DishUpdate, dish_id: int):
        # check id
        query = select(self.model).where(self.model.id == dish_id)
        response = await db.execute(query)
        current_obj = response.scalar_one_or_none()
        if current_obj is None:
            return None, "Not found dish with this id", None
        # check name
        if update_data.name is not None:
            query = select(self.model).where(self.model.name == update_data.name, self.model.id != dish_id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is not None:
                return None, "А dish with that name already exists", None
        if update_data.promo_id is not None:
            query = select(Promo).where(Promo.id == update_data.promo_id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is None:
                return None, "Not found promo with this id", None
        objects = await self.update(db_session=db, obj_current=current_obj, obj_new=update_data)
        return objects, 0, None

    async def check_name(self, *, witch_name: str):
        if witch_name not in ["main_photo", "photo_1", "photo_2"]:
            return f"Incorrect witch photo name '{witch_name}'!"


crud_dish = CrudDish(Dish)
