import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from server.crud import crud_server
from server.getters import getting_server
from server.schemas import ServerCreate, ServerUpdate


# from old_code.auth.base_config import fastapi_users
# from old_code.auth.models import User
# current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
# current_active_user = fastapi_users.current_user(active=True)

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
        limit: int = 100,
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_server.get_all_ips_addresses(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_server(obj) for obj in objects])


@router.get(
            path="/{server_id}",
            response_model=SingleEntityResponse,
            name='get_server',
            description='Вывод серверов по идентификатору'
            )
async def get_server(
        server_id: int,
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_server.get_server_by_id(db=session, id=server_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_server(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_server',
             description='Добавить сервер'
             )
async def add_server(
        new_data: ServerCreate,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_server.add_server(db=session, new_data=new_data)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_server(obj=obj))


@router.put(path="/{server_id}",
            response_model=SingleEntityResponse,
            name='update_server',
            description='Изменить server'
            )
async def update_server(
        update_data: ServerUpdate,
        server_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_server.update_server(db=session, update_data=update_data, id=server_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_server(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
