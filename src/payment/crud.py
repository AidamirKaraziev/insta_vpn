from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import STATUS_DONE, STATUS_ERROR, STATUS_CREATE
from core.base_crud import CRUDBase
from payment.models import Payment
from payment.schemas import PaymentUpdate, PaymentCreate
from referent.crud import crud_referent


class CrudPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    obj_name = "Payment"
    not_found_id = {"num": 404, "message": f"{obj_name}: не нашли с таким id"}
    # name_is_exist = {"num": 403, "message": f"А {obj_name} with that name already exists"}
    id_is_exist = {"num": 403, "message": f"{obj_name}: с таким id уже есть"}
    payment_status_is_error = {"num": 403, "message": f"{obj_name}: у этой оплаты статус Error"}
    payment_status_is_done = {"num": 403, "message": f"{obj_name}:  у этой оплаты статус Done"}

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

    async def execution_of_payment(self, *, db: AsyncSession, id: UUID4):
        """
            Проверяем id, если такого нет - возвращает ошибку.
            Если у этой записи статус - 'Ошибка', выводим соответствующую.
            Если у этой записи статус - 'Готов', выводим соответствующую.
            Если не получилось пополнить баланс референту, выводим соответствующую ошибку.
        """
        this_obj, code, indexes = await self.get_payment_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        if this_obj.status_id == STATUS_DONE.id:
            return None, self.payment_status_is_done, None
        elif this_obj.status_id == STATUS_ERROR.id:
            return None, self.payment_status_is_error, None
        elif this_obj.status_id == STATUS_CREATE.id:
            # изменяем баланс референту
            referent, code, indexes = await crud_referent.change_balance(
                db=db, id=this_obj.referent_id, amount=this_obj.amount)
            if code != 0:
                error_status = PaymentUpdate(status_is=STATUS_ERROR.id)
                await super().update(db_session=db, obj_current=this_obj, obj_new=error_status)
                # TODO запись в лог
                return None, code, None
        update_data = PaymentUpdate(status_id=STATUS_DONE.id)
        objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
        return objects, 0, None


crud_payment = CrudPayment(Payment)
