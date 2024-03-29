import logging
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from config import STATUS_CREATE, PAYMENT_TYPE_DECREASE
from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session

from auth.base_config import fastapi_users
from auth.models import User
from payment.crud import crud_payment
from payment.getters import getting_payment
from payment.schemas import PaymentCreate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_payments',
            description='Получение списка всех выплат'
            )
async def get_payments(
        skip: int = 0,
        limit: int = 1000,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_payment.get_all(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_payment(obj) for obj in objects])


@router.get(
            path='/get-payments-by/{status_id}{payment_type_id}',
            response_model=ListOfEntityResponse,
            name='get_by_status_id_and_payment_type_id',
            description='Получение списка платежей отфильтрованных по status_id и payment_type_id.'
            )
async def get_by_status_id_and_payment_type_id(
        payment_type_id: int,
        status_id: Optional[int] = STATUS_CREATE.id,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_payment.get_by_status_id_and_payment_type_id(
        db=session, status_id=status_id, payment_type_id=payment_type_id)

    await get_raise_new(code)
    return ListOfEntityResponse(data=[getting_payment(obj) for obj in objects])


@router.get(
            path="/{payment_id}",
            response_model=SingleEntityResponse,
            name='get_payment',
            description='Вывод выплаты по id'
            )
async def get_payment(
        payment_id: UUID4,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_payment.get_payment_by_id(db=session, id=payment_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_payment(obj=obj))


@router.post(path="/payment-withdrawal/",
             response_model=SingleEntityResponse,
             name='create_payment_withdrawal',
             description='Создать платеж на вывод средств'
             )
async def create_payment_withdrawal(
        new_data: PaymentCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    new_data.payment_type_id = PAYMENT_TYPE_DECREASE.id
    obj, code, indexes = await crud_payment.create_payment(db=session, new_data=new_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_payment(obj=obj))


@router.put(path="/execution/{payment_id}",
            response_model=SingleEntityResponse,
            name='execution_payment',
            description='Исполнить оплату'
            )
async def execution_payment(
        payment_id: UUID4,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_payment.execution_of_payment(db=session, id=payment_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_payment(obj=obj))


@router.put(path="/make-all-new/{payment_type_id}",
            response_model=SingleEntityResponse,
            name='make_all_new_payments',
            description='Исполнить все новые платежи'
            )
async def make_all_new_payments(
        payment_type_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    data, code, indexes = await crud_payment.make_all_new_payments(
        db=session, payment_type_id=payment_type_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=data)

if __name__ == "__main__":
    logging.info('Running...')
