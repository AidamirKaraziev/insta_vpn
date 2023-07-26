import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import fastapi_users
from auth.models import User
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from old_code.order.crud import crud_order
from old_code.order.getters import getting_order
from old_code.order.schemas import OrderCreate, OrderUpdate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
current_active_user = fastapi_users.current_user(active=True)

router = APIRouter(
    prefix="/order",
    tags=["Order"]
)


@router.get(
    path='/orders',
    response_model=ListOfEntityResponse,
    name='get_orders',
    description='Получение списка всех заказов'
)
async def get_orders(
        request: Request,
        limit: int = 100,
        skip: int = 0,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    orders, code, indexes = await crud_order.get_all_orders(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_order(obj=order, request=request) for order in orders])


@router.get(
    path="/{order_id}",
    response_model=SingleEntityResponse,
    name='get_order_by_id',
    description='Вывод заказа по идентификатору'
)
async def get_order_by_id(
        request: Request,
        order_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    order, code, indexes = await crud_order.get_order_by_id(db=session, order_id=order_id)
    if code != 0:
        raise HTTPException(status_code=404, detail="Resource with this ID does not exist")
    return SingleEntityResponse(data=getting_order(obj=order, request=request))


@router.post(
    path="/",
    response_model=SingleEntityResponse,
    name='create_order',
    description='Добавление заказа'
)
async def create_order(
        request: Request,
        new_data: OrderCreate,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_order.create_order(db=session, new_data=new_data)
    if code != 0:
        raise HTTPException(status_code=409, detail=code)
    return SingleEntityResponse(data=getting_order(obj=obj, request=request))


@router.put(
    path="/{order_id}",
    response_model=SingleEntityResponse,
    name='update_order',
    description='Изменение заказа'
)
async def update_order(
        request: Request,
        update_data: OrderUpdate,
        order_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    order, code, indexes = await crud_order.update_order(db=session,
                                                         update_data=update_data,
                                                         order_id=order_id)
    if code != 0:
        raise HTTPException(status_code=404, detail=code)
    return SingleEntityResponse(data=getting_order(obj=order, request=request))


if __name__ == "__main__":
    logging.info('Running...')
