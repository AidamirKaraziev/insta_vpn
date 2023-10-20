import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from auth.base_config import fastapi_users
from auth.models import User

from static_key.crud import crud_static_key
from static_key.getters import getting_static_key

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/static_key",
    tags=["StaticKey"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_static_key',
            description='Получение списка всех ключей'
            )
async def get_static_key(
        limit: int = 1000,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_static_key.get_all_static_keys(db=session, skip=0, limit=limit)
    return ListOfEntityResponse(data=[getting_static_key(obj) for obj in objects])


@router.get(
            path="/{static_key_id}",
            response_model=SingleEntityResponse,
            name='get_static_key',
            description='Вывод ключа по идентификатору'
            )
async def get_static_key(
        static_key_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_static_key.get_static_key_by_id(db=session, id=static_key_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_static_key(obj=obj))


@router.get(
            path="/by/{server_id}",
            response_model=ListOfEntityResponse,
            name='get_static_keys_by_server_id',
            description='Вывод статических ключей по идентификатору сервера'
            )
async def get_static_keys_by_server_id(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_static_key.get_static_keys_by_server_id(db=session, server_id=server_id)
    await get_raise_new(code)
    return ListOfEntityResponse(data=[getting_static_key(obj) for obj in objects])


@router.post(path="/create/{server_id}",
             response_model=SingleEntityResponse,
             name='add_static_keys',
             description='Добавить ключ'
             )
async def add_static_keys(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    key, code, indexes = await crud_static_key.create_key(db=session, server_id=server_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_static_key(obj=key))


if __name__ == "__main__":
    logging.info('Running...')
