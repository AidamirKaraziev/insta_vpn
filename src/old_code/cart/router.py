import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from old_code.auth.base_config import fastapi_users
from old_code.auth.models import User
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from old_code.cart.crud import crud_cart
from old_code.cart.getters import getting_cart
from old_code.cart.schemas import CartCreate, CartUpdate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
current_active_user = fastapi_users.current_user(active=True)

router = APIRouter(
    prefix='/cart',
    tags=['Cart']
)


@router.get(
    path='/item/{item_id}',
    response_model=SingleEntityResponse,
    name='get_item_by_id',
    description='Вывод элемента корзины по его id'
)
async def get_item_by_id(
        request: Request,
        item_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_cart.get_item_by_id(db=session, item_id=item_id)
    if code != 0:
        raise HTTPException(status_code=404, detail=code)
    return SingleEntityResponse(data=getting_cart(obj=obj, request=request))


@router.get(
    path="/{order_id}",
    response_model=ListOfEntityResponse,
    name='get_cart_by_order_id',
    description='Вывод всех элементов корзины по order_id'
)
async def get_cart_by_order_id(
        request: Request,
        order_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_cart.get_cart_by_order_id(db=session, order_id=order_id)
    if code != 0:
        raise HTTPException(status_code=404, detail=code)
    return ListOfEntityResponse(data=[getting_cart(obj=item, request=request) for item in objects])


@router.post(
    path="/",
    response_model=SingleEntityResponse,
    name='create_cart_item',
    description='Добавление позиции в корзину'
)
async def create_cart_item(
        request: Request,
        new_data: CartCreate,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    if user.is_superuser is True:
        raise HTTPException(status_code=409, detail="Корзину заполняют только клиенты!")
    obj, code, indexes = await crud_cart.create_item_cart(db=session, new_data=new_data)
    if code != 0:
        raise HTTPException(status_code=409, detail=code)
    return SingleEntityResponse(data=getting_cart(obj=obj, request=request))


@router.put(
    path="/{item_id}",
    response_model=SingleEntityResponse,
    name='update_cart_item',
    description='Изменение позиции в корзине'
)
async def update_cart_item(
        request: Request,
        update_data: CartUpdate,
        item_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    # добавить проверку чтобы клиент не смог менять не свой заказ

    obj, code, indexes = await crud_cart.update_item_cart(db=session,
                                                          update_data=update_data,
                                                          item_id=item_id)
    if code != 0:
        raise HTTPException(status_code=404, detail=code)
    return SingleEntityResponse(data=getting_cart(obj=obj, request=request))


@router.delete(
    path="/{item_id}",
    response_model=SingleEntityResponse,
    name='delete_cart_item',
    description='Изменение позиции в корзине'
)
async def delete_cart_item(
        request: Request,
        item_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_cart.delete_item_cart(db=session, item_id=item_id)
    if code != 0:
        raise HTTPException(status_code=404, detail=code)
    return SingleEntityResponse(data=getting_cart(obj=obj, request=request))

if __name__ == "__main__":
    logging.info('Running...')
