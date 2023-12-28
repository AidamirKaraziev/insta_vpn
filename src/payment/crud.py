from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import STATUS_DONE, STATUS_ERROR, STATUS_CREATE
from core.base_crud import CRUDBase
from payment.models import Payment
from payment.schemas import PaymentUpdate, PaymentCreate
from payment_type.crud import crud_payment_type
from referent.crud import crud_referent
from status.crud import crud_status


class CrudPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    obj_name = "Payment"
    not_found_id = {"num": 404, "message": f"{obj_name}: не нашли с таким id"}
    # name_is_exist = {"num": 403, "message": f"А {obj_name} with that name already exists"}
    id_is_exist = {"num": 403, "message": f"{obj_name}: с таким id уже есть"}
    payment_status_is_error = {"num": 403, "message": f"{obj_name}: у этой оплаты статус Error"}
    payment_status_is_done = {"num": 403, "message": f"{obj_name}:  у этой оплаты статус Done"}
    bad_amount = {"num": 403, "message": f"{obj_name}: amount должно быть больше нуля."}

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

    async def get_by_status_id_and_payment_type_id(self, *, db: AsyncSession, status_id: int, payment_type_id: int):
        """
            Получение списка платежей отфильтрованных по status_id и payment_type_id.
            Если нет такого status_id, выводит ошибку с описанием.
            Если нет такого payment_type_id, выводит ошибку с описанием.
        """
        status, code, indexes = await crud_status.get_status_by_id(db=db, id=status_id)
        if code != 0:
            return None, code, None
        payment_type, code, indexes = await crud_payment_type.get_by_id(db=db, id=payment_type_id)
        if code != 0:
            return None, code, None
        query = select(self.model).where(
            self.model.status_id == status_id, self.model.payment_type_id == payment_type.id)
        resp = await db.execute(query)
        objects = resp.scalars().all()
        return objects, 0, None

    async def create_payment(self, *, db: AsyncSession, new_data: PaymentCreate):
        """
            Генерируем id: uuid
            Проверяем id, если такой есть - возвращает ошибку.
            Проверяем если рефрент по referent_id, если такого нет вернет ошибку.

            spb_number: str - никаких проверок нет, я только сохраняю.
            card_number: Optional[str] - я сохраняю, логика в боте.
            payment_type_id: Optional[int] - если такого нет выводит ошибку.
            status_id: Optional[int] = 1(Создан)
        """
        uuid_value = uuid4()
        new_data.id = uuid_value
        # check id
        obj, code, indexes = await self.get_payment_by_id(db=db, id=uuid_value)
        if obj:
            return None, self.id_is_exist, None
        referent, code, indexes = await crud_referent.get_referent_by_id(
            db=db, id=new_data.referent_id)
        if code != 0:
            return None, code, None
        if new_data.amount <= 0:
            return None, self.bad_amount, None
        payment_type, code, indexes = await crud_payment_type.get_by_id(db=db, id=new_data.payment_type_id)
        if code != 0:
            return None, code, None
        new_data.status_id = STATUS_CREATE.id
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def execution_of_payment(self, *, db: AsyncSession, id: UUID4):
        """
            Проверяем payment_id, если такого нет - возвращает ошибку.
            Если у этой записи статус - 'Ошибка', выводим соответствующую.
            Если у этой записи статус - 'Готов', выводим соответствующую.
            Если не получилось изменить баланс референту:
                возвращаем ошибку, изменяемый объект и изменяем статус платежа на 'ошибка'.
        """
        this_obj, code, indexes = await self.get_payment_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        if this_obj.status_id == STATUS_DONE.id:
            return None, self.payment_status_is_done, None
        elif this_obj.status_id == STATUS_ERROR.id:
            return None, self.payment_status_is_error, None
        elif this_obj.status_id == STATUS_CREATE.id:
            # изменяем баланс референту, указываем сумму и тип оплаты
            referent, code, indexes = await crud_referent.change_balance(
                db=db, id=this_obj.referent_id, amount=this_obj.amount, payment_type_id=this_obj.payment_type_id)

            if code != 0:
                error_status = PaymentUpdate(status_id=STATUS_ERROR.id)
                this_obj = await super().update(db_session=db, obj_current=this_obj, obj_new=error_status)
                # TODO запись в лог
                return this_obj, code, None
        update_data = PaymentUpdate(status_id=STATUS_DONE.id)
        this_obj = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
        return this_obj, 0, None

    async def make_all_new_payments(self, *, db: AsyncSession, payment_type_id: int):
        """
            Получение списка платежей отфильтрованных по status_id = STATUS_CREATE.id.
            Если нет такого status_id, выводит ошибку с описанием.
        """
        done_list = []
        error_list = []
        created_payments, code, indexes = await self.get_by_status_id_and_payment_type_id(
            db=db, status_id=STATUS_CREATE, payment_type_id=payment_type_id)
        if code != 0:
            return None, code, None
        for payment in created_payments:
            res, code, indexes = await self.execution_of_payment(db=db, id=payment.id)
            if code == 0:
                done_list.append(res)
            else:
                error_list.append(res)
        return {"Готово": done_list,
                "Ошибка": error_list}, 0, None


crud_payment = CrudPayment(Payment)
