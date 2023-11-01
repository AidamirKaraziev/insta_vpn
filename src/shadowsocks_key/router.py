import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from auth.base_config import fastapi_users
from auth.models import User
from shadowsocks_key.crud import crud_shadowsocks_key
from shadowsocks_key.getters import getting_shadowsocks_key

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/shadowsocks_key",
    tags=["ShadowsocksKey"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_shadowsocks_key',
            description='Получение списка всех ключей'
            )
async def get_shadowsocks_key(
        limit: int = 1000,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_shadowsocks_key.get_all_shadowsocks_keys(db=session, skip=0, limit=limit)
    return ListOfEntityResponse(data=[getting_shadowsocks_key(obj) for obj in objects])


@router.get(
            path="/{shadowsocks_key_id}",
            response_model=SingleEntityResponse,
            name='get_shadowsocks_key',
            description='Вывод ключа по идентификатору'
            )
async def get_shadowsocks_key(
        shadowsocks_key_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_shadowsocks_key.get_shadowsocks_key_by_id(db=session, id=shadowsocks_key_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_shadowsocks_key(obj=obj))


@router.get(
            path="/by/{server_id}",
            response_model=ListOfEntityResponse,
            name='get_shadowsocks_keys_by_server_id',
            description='Вывод статических ключей по идентификатору сервера'
            )
async def get_shadowsocks_keys_by_server_id(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_shadowsocks_key.get_shadowsocks_keys_by_server_id(db=session, server_id=server_id)
    await get_raise_new(code)
    return ListOfEntityResponse(data=[getting_shadowsocks_key(obj) for obj in objects])


@router.post(path="/create/{server_id}",
             response_model=SingleEntityResponse,
             name='add_shadowsocks_keys',
             description='Добавить ключ'
             )
async def add_shadowsocks_keys(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    key, code, indexes = await crud_shadowsocks_key.create_key(db=session, server_id=server_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_shadowsocks_key(obj=key))


@router.get(path="/free-keys-output/",
            response_model=SingleEntityResponse,
            name='output_how_many_free_keys',
            description='Вывести сколько есть свободных ключей'
            )
async def output_how_many_free_keys(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    quantity_free_keys, code, indexes = await crud_shadowsocks_key.get_quantity_free_keys(db=session)
    await get_raise_new(code)
    response = f"Свободных ключей: {quantity_free_keys}"
    return SingleEntityResponse(data=response)

# TODO отложенная задача, которая отправляет уведомление если количество хороших ключей опускается до 100 шт


if __name__ == "__main__":
    logging.info('Running...')
