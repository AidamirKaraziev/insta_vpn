import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new, raise_schemas
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
from outline_key.crud import crud_outline_key
from server.crud import crud_server
# from server.crud import crud_server
from server.getters import getting_server
# from server.schemas import ServerCreate, ServerUpdate
from auth.base_config import fastapi_users
from auth.models import User
from server.schemas import OutlineServerCreate, ServerUpdate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/server",
    tags=["Server"]
)
# TODO get servers by vpn_type_id
# TODO activate vless server
# TODO deactivate vless server
# TODO delete vless server

# TODO create vless server with keys
# TODO update vless server
# TODO activate vless server
# TODO deactivate vless server


# TODO функция по изменению максимального количества для Outline
# TODO create shadowsocks server with keys
# TODO update vless server
# TODO activate shadowsocks server
# TODO deactivate shadowsocks server


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


@router.post(path="/create-outline-server/",
             response_model=SingleEntityResponse,
             name='add_outline_server_create_keys',
             description='Добавить Outline сервер и создать ключи для него в количестве max_client'
             )
async def add_outline_server_create_keys(
        new_data: OutlineServerCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    # TODO мне не нравится, логика - переделать!
    server, code, indexes = await crud_server.add_outline_server(db=session, new_data=new_data)
    await get_raise_new(code)
    keys, code, indexes = await crud_outline_key.creating_keys_for_a_server(db=session, server_id=server.id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_server(obj=server))


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


@router.get(path="/deactivate-outline/{server_id}",
            response_model=SingleEntityResponse,
            name='deactivate_outline_server_and_keys',
            description='Деактивация Outline сервера и всех его ключей'
            )
async def deactivate_outline_server_and_keys(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_server.deactivate_server(db=session, id=server_id)
    await get_raise_new(code)
    keys, code, indexes = await crud_outline_key.deactivate_keys_by_server_id(db=session, server_id=server_id)
    await get_raise_new(code)
    update_data = ServerUpdate(is_active=False)
    server, code, indexes = await crud_server.update_server(db=session, id=server_id, update_data=update_data)
    await get_raise_new(code)
    d = f"""Сервер {obj.name} деактивирован и его Outline ключи в количестве: {len(keys)}"""
    return SingleEntityResponse(data=d)


@router.get(path="/activate-outline/{server_id}",
            response_model=SingleEntityResponse,
            name='activate_outline_server_and_keys',
            description='Активация Outline сервера и всех его ключей'
            )
async def activate_outline_server_and_keys(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_server.activate_server(db=session, id=server_id)
    await get_raise_new(code)
    keys, code, indexes = await crud_outline_key.activate_keys_by_server_id(db=session, server_id=server_id)
    await get_raise_new(code)
    d = f"""Сервер {obj.name} активирован и его Outline ключи в количестве: {len(keys)}"""
    return SingleEntityResponse(data=d)


if __name__ == "__main__":
    logging.info('Running...')
