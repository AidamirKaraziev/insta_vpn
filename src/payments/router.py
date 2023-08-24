import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from payments.crud import crud_payment
from payments.getters import getting_payment
from payments.schemas import PaymentCreate


# from old_code.auth.base_config import fastapi_users
# from old_code.auth.models import User
# current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
# current_active_user = fastapi_users.current_user(active=True)

router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_payments',
            description='Получение списка всех оплат'
            )
async def get_payments(
        skip: int = 0,
        limit: int = 100,
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_payment.get_all_payments(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_payment(obj) for obj in objects])


@router.get(
            path="/{payment_id}",
            response_model=SingleEntityResponse,
            name='get_payment',
            description='Вывод оплаты по идентификатору'
            )
async def get_payment(
        payment_id: int,
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_payment.get_payment_by_id(db=session, id=payment_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_payment(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_payment',
             description='Добавить оплату'
             )
async def add_payment(
        new_data: PaymentCreate,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_payment.add_payment(db=session, new_data=new_data)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_payment(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
