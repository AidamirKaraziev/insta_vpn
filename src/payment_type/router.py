import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session

from auth.base_config import fastapi_users
from auth.models import User
from payment_type.crud import crud_payment_type
from payment_type.getters import getting_payment_type
from payment_type.schemas import PaymentTypeUpdate, PaymentTypeCreate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)

"""
    Эти апи нигде не нужны, но полностью написаны и протестированы.
    - get_all
    - get_by_id
    - add_new
    - update_payment_type
"""
router = APIRouter(
    prefix="/payment-type",
    tags=["Payment Type"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_payment_type',
            description='Получение списка всех типов оплат'
            )
async def get_payment_types(
        skip: int = 0,
        limit: int = 100,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_payment_type.get_all(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_payment_type(obj) for obj in objects])


@router.get(
            path="/{payment_type_id}",
            response_model=SingleEntityResponse,
            name='get_payment_type',
            description='Вывод типа оплаты по id'
            )
async def get_payment_type(
        payment_type_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_payment_type.get_by_id(db=session, id=payment_type_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_payment_type(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_payment_type',
             description='Добавить новый тип оплаты'
             )
async def add_payment_type(
        new_data: PaymentTypeCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_payment_type.add_new(db=session, new_data=new_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_payment_type(obj=obj))


@router.put(path="/{payment_type_id}",
            response_model=SingleEntityResponse,
            name='update_payment_type',
            description='Изменить данные типа оплаты'
            )
async def update_payment_type(
        update_data: PaymentTypeUpdate,
        payment_type_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_payment_type.update_payment_type(
        db=session, update_data=update_data, id=payment_type_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_payment_type(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
