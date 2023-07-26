from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from old_code.cart.models import Cart
from old_code.cart.schemas import CartCreate, CartUpdate

from old_code.dish.models import Dish
from old_code.order.models import Order

from core.base_crud import CRUDBase


class CrudCart(CRUDBase[Cart, CartCreate, CartUpdate]):

    async def get_item_by_id(self, *, db: AsyncSession, item_id: int):
        obj = await self.get(db=db, id=item_id)
        if obj is None:
            return None, "Not found item with this id", None
        return obj, 0, None

    async def get_cart_by_order_id(self, *, db: AsyncSession, order_id: int):
        db_session = db or self.db.session
        query = select(self.model).where(self.model.order_id == order_id)
        response = await db_session.execute(query)
        objects = response.scalars().all()
        if objects is None:
            return None, "Not found cart with this id", None
        return objects, 0, None

    async def get_all_carts(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await self.get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def create_item_cart(self, *, db: AsyncSession, new_data: CartCreate):

        # check dish exist
        query = select(Dish).where(Dish.id == new_data.dish_id)
        response = await db.execute(query)
        if response.scalar_one_or_none() is None:
            return None, "Not found dish with this id", None

        # check dish exist in this cart
        query = select(self.model).where(self.model.order_id == new_data.order_id,
                                         self.model.dish_id == new_data.dish_id)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, "There is already this dish in this cart", None

        objects = await self.create(db_session=db, obj_in=new_data)

        # Обновляем сумму в позиции
        objects.sum = objects.quantity * objects.dish.price
        db.add(objects)
        await db.commit()
        await db.refresh(objects)

        # Обновляем сумму в заказе
        query = select(func.sum(Cart.sum)).where(Cart.order_id == objects.order_id)
        total_sum = await db.scalar(query)

        order_object = await db.get(Order, objects.order_id)
        order_object.sum = total_sum

        await db.merge(order_object)
        await db.commit()

        return objects, 0, None

    async def update_item_cart(self, *, db: AsyncSession, update_data: CartCreate, item_id: int):
        # check id
        query = select(self.model).where(self.model.id == item_id)
        response = await db.execute(query)
        current_obj = response.scalar_one_or_none()
        if current_obj is None:
            return None, "Not found item_cart with this id", None
        objects = await self.update(db_session=db, obj_current=current_obj, obj_new=update_data)

        # refresh item sum
        objects.sum = objects.quantity * objects.dish.price
        db.add(objects)
        await db.commit()
        await db.refresh(objects)

        # refresh order sum
        query = select(func.sum(Cart.sum)).where(Cart.order_id == objects.order_id)
        total_sum = await db.scalar(query)

        order_object = await db.get(Order, objects.order_id)
        order_object.sum = total_sum

        await db.merge(order_object)
        await db.commit()

        return objects, 0, None

    async def delete_item_cart(self, *, db: AsyncSession, item_id: int):
        # check id
        obj = await self.get(db=db, id=item_id)
        if obj is None:
            return None, "Not found item with this id", None

        await self.delete(id=item_id, db=db)

        # refresh order sum
        query = select(func.sum(Cart.sum)).where(Cart.order_id == obj.order_id)
        total_sum = await db.scalar(query)

        order_object = await db.get(Order, obj.order_id)
        order_object.sum = total_sum

        await db.merge(order_object)
        await db.commit()

        return obj, 0, None


crud_cart = CrudCart(Cart)
