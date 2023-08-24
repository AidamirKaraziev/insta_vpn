import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_crud import CRUDBase
from payments.models import Payment
from payments.schemas import PaymentCreate, PaymentUpdate
from profiles.crud import crud_profile
from tariff.crud import crud_tariff
from utils.time_stamp import to_timestamp, date_from_timestamp


class CrudPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    obj_name = "Payment"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}

    async def get_payment_by_id(self, *, db: AsyncSession, id: int):
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_all_payments(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def add_payment(self, *, db: AsyncSession, new_data: PaymentCreate):
        profile, code, indexes = await crud_profile.get_profile_by_id(db=db, id=new_data.profile_id)
        if code != 0:
            return None, code, None
        tariff, code, indexes = await crud_tariff.get_tariff_by_id(db=db, id=new_data.tariff_id)
        if code != 0:
            return None, code, None
        # определяю корректную дату отсчета: либо сегодня, либо дата окончания. Что новее
        unix_today = to_timestamp(datetime.datetime.today())
        unix_date_end = to_timestamp(profile.date_end)
        largest_date = max([unix_date_end, unix_today])
        new_unix_date = largest_date + tariff.period_unix
        date = date_from_timestamp(new_unix_date)

        new_date_end = datetime.date(date.year, date.month, date.day)
        update_profile_date_end = {"date_end": new_date_end}

        obj, code, indexes = await crud_profile.update_profile(db=db, update_data=update_profile_date_end, id=profile.id)
        if code != 0:
            return None, code, None

        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None


crud_payment = CrudPayment(Payment)
