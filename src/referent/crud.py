from typing import Union

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import PAYMENT_TYPE_INCREASE, GENERAL_PARTNER, NATIVE_REFERENT_TYPE, BASE_REFERENT_GIFT_DAYS, \
    PAYMENT_TYPE_DECREASE
from core.base_crud import CRUDBase
from partner.crud import crud_partner

from referent.models import Referent
from referent.schemas import ReferentUpdate, ReferentNativeCreate, ReferentCompanyCreate
from referent_type.crud import crud_referent_type


class CrudReferent(CRUDBase[Referent, Union[ReferentNativeCreate, ReferentCompanyCreate], ReferentUpdate]):
    obj_name = "Референт"
    not_found_id = {"num": 404, "message": f"Не нашли {obj_name}а с таким id."}
    telegram_id_is_exist = {"num": 403, "message": f"{obj_name} с таким telegram_id уже есть."}
    balance_less_than_zero = {"num": 403, "message": f"{obj_name}: баланс не может быть меньше нуля."}
    cannot_reduce_the_balance_of_non_native = {
        "num": 403, "message": f"{obj_name}: нельзя уменьшать баланс, если референт не нативный."}
    cannot_be_native = {"num": 403, "message": f"{obj_name}: ссылка созданная вручную не может быть нативной."}

    async def get_all_referents(self, *, db: AsyncSession, skip: int, limit: int):
        """
            Выводим список всех референтов.
        """
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def get_referent_by_id(self, *, db: AsyncSession, id: UUID4):
        """
            Проверяем id, если такого нет - возвращает ошибку.
            Возвращаем по id.
        """
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_by_telegram_id(self, *, db: AsyncSession, telegram_id: int):
        """Возвращает список референтов, по телеграм id"""
        res = select(self.model).where(self.model.telegram_id == telegram_id)
        response = await db.execute(res)
        objs = response.scalars().all()
        return objs, 0, None

    async def create_native_referent(self, *, db: AsyncSession, new_data: ReferentNativeCreate):
        """
            telegram_id: int
            gift_days: Optional[int] = BASE_REFERENT_GIFT_DAYS
            partner_id: Optional[int] = GENERAL_PARTNER.id
            referent_type_id = NATIVE_REFERENT_TYPE.id
        """
        res = select(self.model).where(self.model.telegram_id == new_data.telegram_id,
                                       self.model.referent_type_id == NATIVE_REFERENT_TYPE.id)
        response = await db.execute(res)
        referent = response.scalar_one_or_none()
        if referent is not None:
            return referent, 0, None
        else:
            new_data.gift_days = BASE_REFERENT_GIFT_DAYS
            new_data.referent_type_id = NATIVE_REFERENT_TYPE.id
            new_data.partner_id = GENERAL_PARTNER.id

            objects = await super().create(db_session=db, obj_in=new_data)
            return objects, 0, None

    async def change_balance(self, *, db: AsyncSession, id: UUID4, amount: int, payment_type_id: int):
        """
            Amount - это сумма на которую изменится баланс.
            В payment есть проверка чтобы amount был больше нуля.
            Проверяем есть ли такой референт по referent_id, если нет - выводим ошибку с описанием.
            Balance проверка, чтобы баланс не мог стать отрицательным.
            Уменьшить баланс могут только нативные клиенты.
        """
        this_obj, code, indexes = await self.get_referent_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        balance = int(this_obj.balance)
        if payment_type_id == PAYMENT_TYPE_INCREASE.id:  # Увеличить баланс
            balance = int(this_obj.balance) + amount
        elif payment_type_id == PAYMENT_TYPE_DECREASE.id:  # Уменьшить баланс
            if this_obj.referent_type_id != NATIVE_REFERENT_TYPE.id:
                return None, self.cannot_reduce_the_balance_of_non_native, None
            balance = balance - amount
            if balance < 0:
                return None, self.balance_less_than_zero, None
        # запись нового баланса
        update_data = ReferentUpdate(balance=balance)
        objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
        return objects, 0, None

    async def create_referent_for_us(self, *, db: AsyncSession, new_data: ReferentCompanyCreate):
        """
            gift_days: Optional[int] - указывать при создании.
            partner_id: Optional[int] - указывается партнер, который ответственен.
            referent_type_id: Optional[int] - указывается в апи.

            description: Optional[str] - пишется описание рекламной компании.
            budget_amount: Optional[int] - сумма затраченная на рекламу.
        """
        referent_type, code, indexes = await crud_referent_type.get_referent_type_by_id(
            db=db, id=new_data.referent_type_id)
        if code != 0:
            return None, code, None
        if referent_type.id == NATIVE_REFERENT_TYPE.id:
            return None, self.cannot_be_native, None
        partner, code, indexes = await crud_partner.get_partner_by_id(db=db, id=new_data.partner_id)
        if code != 0:
            return None, code, None
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None


crud_referent = CrudReferent(Referent)
