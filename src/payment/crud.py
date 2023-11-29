from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_crud import CRUDBase
from payment.models import Payment
from payment.schemas import PaymentUpdate, PaymentCreate
from referent.crud import crud_referent


class CrudPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    obj_name = "Payment"
    not_found_id = {"num": 404, "message": f"{obj_name}: не нашли с таким id"}
    # name_is_exist = {"num": 403, "message": f"А {obj_name} with that name already exists"}
    id_is_exist = {"num": 403, "message": f"{obj_name}: с таким id уже есть"}

    async def get_all(self, *, db: AsyncSession, skip: int, limit: int):
        """
            Выводим список всех выплат.
        """
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def get_payment_by_id(self, *, db: AsyncSession, id: UUID4):
        """
            Проверяем id, если такого нет - возвращает ошибку.
            Возвращаем по id.
        """
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def create_payment(self, *, db: AsyncSession, new_data: PaymentCreate):
        """
            Генерируем id: uuid
            Проверяем id, если такой есть - возвращает ошибку.
            В change_balance проверяем referent_id: если такого нет вернет ошибку.

            spb_number: str - никаких проверок нет(возможно надо добавить)
            card_number: Optional[str] - возможно вообще удалить
            status_id: Optional[int] = 1(Создан)
        """
        uuid_value = uuid4()
        new_data.id = uuid_value
        # check id
        obj, code, indexes = await self.get_payment_by_id(db=db, id=uuid_value)
        if obj:
            return None, self.id_is_exist, None
        # если такого референта нет вернет ошибку, если sum больше баланса вернет ошибку
        referent, code, indexes = await crud_referent.get_referent_by_id(
            db=db, id=new_data.referent_id)
        if code != 0:
            return None, code, None
        new_data.status_id = 1
        # TODO Проверка на валидацию spb_number
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None


crud_payment = CrudPayment(Payment)
#

# async def update_payment(self, *, db: AsyncSession, update_data: PaymentUpdate, id: int):
#     """
#         Проверяем id, если такого нет - возвращает ошибку.
#         Проверяем update_data.id, если такой есть не у изменяемого объекта - возвращает ошибку.
#         Проверяем name, если такой есть - возвращает ошибку.
#     """
#     this_obj, code, indexes = await self.get_payment_by_id(db=db, id=id)
#     if code != 0:
#         return None, code, None
#     if update_data.id is not None and this_obj.id != update_data.id:
#         obj, code, indexes = await self.get_payment_by_id(db=db, id=update_data.id)
#         if obj is not None:
#             return None, self.id_is_exist, None
#     # check name
#     if update_data.name is not None:
#         query = select(self.model).where(self.model.name == update_data.name, self.model.id != id)
#         response = await db.execute(query)
#         if response.scalar_one_or_none() is not None:
#             return None, self.name_is_exist, None
#     objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
#     return objects, 0, None
