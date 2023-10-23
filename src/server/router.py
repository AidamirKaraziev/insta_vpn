import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new, raise_schemas
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
from server.crud import crud_server
from server.getters import getting_server
from server.schemas import ServerCreate, ServerUpdate
from static_key.crud import crud_static_key
from utils.utils import update_fact_clients
from auth.base_config import fastapi_users
from auth.models import User

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/server",
    tags=["Server"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_servers',
            description='Получение списка всех серверов'
            )
async def get_servers(
        skip: int = 0,
        limit: int = 1000,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_server.get_all_servers(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_server(obj) for obj in objects])


@router.get(
            path="/{server_id}",
            response_model=SingleEntityResponse,
            name='get_server',
            description='Вывод серверов по идентификатору'
            )
async def get_server(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_server.get_server_by_id(db=session, id=server_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_server(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_server_create_keys',
             description='Добавить сервер и создать ключи для него'
             )
async def add_server_create_keys(
        new_data: ServerCreate,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    try:
        server, code, indexes = await crud_server.add_server(db=session, new_data=new_data)
        await get_raise_new(code)
        keys, code, indexes = await crud_static_key.creating_keys_for_a_server(db=session, server_id=server.id)
        await get_raise_new(code)
        return SingleEntityResponse(data=getting_server(obj=server))
    except Exception as ex:
        await get_raise_new(raise_schemas(ex))


@router.put(path="/{server_id}",
            response_model=SingleEntityResponse,
            name='update_server',
            description='Изменить server'
            )
async def update_server(
        update_data: ServerUpdate,
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_server.update_server(db=session, update_data=update_data, id=server_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_server(obj=obj))


@router.delete(path="/{server_id}",
               response_model=SingleEntityResponse,
               name='delete_server',
               description='Удалить сервер и все связанные с ним ключи'
               )
async def delete_server(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_server.delete_server(db=session, id=server_id)
    await get_raise_new(code)
    return OkResponse()


# TODO change to -> how mach used key
@router.get(path="/update-fact-client/",
            response_model=SingleEntityResponse,
            name='update_fact_client',
            description='Записать в БД фактическое количество клиентов'
            )
async def update_fact_client(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    servers, code, indexes = await update_fact_clients(db=session)
    await get_raise_new(code)
    return SingleEntityResponse(data=servers)


@router.get(path="/deactivate/{server_id}",
            response_model=SingleEntityResponse,
            name='deactivate_server_and_keys',
            description='Деактивация сервера и всех его ключей'
            )
async def deactivate_server_and_keys(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_server.deactivate_server(db=session, id=server_id)
    await get_raise_new(code)
    keys, code, indexes = await crud_static_key.deactivate_keys_by_server_id(db=session, server_id=server_id)
    await get_raise_new(code)
    return OkResponse()


@router.get(path="/activate/{server_id}",
            response_model=SingleEntityResponse,
            name='activate_server_and_keys',
            description='Активация сервера и всех его ключей'
            )
async def deactivate_server_and_keys(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_server.activate_server(db=session, id=server_id)
    await get_raise_new(code)
    keys, code, indexes = await crud_static_key.activate_keys_by_server_id(db=session, server_id=server_id)
    await get_raise_new(code)
    return OkResponse()


if __name__ == "__main__":
    logging.info('Running...')
