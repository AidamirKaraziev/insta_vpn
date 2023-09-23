import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import FREE_TRAFFIC, LIMIT_SERVERS
from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
from profiles.crud import crud_profile
from profiles.getters import getting_profile
from server.crud import crud_server
from server.getters import getting_server
from utils import utils
from auth.base_config import fastapi_users
from auth.models import User

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/tools",
    tags=["Tools"]
)


@router.get(
            path="/ping/",
            response_model=ListOfEntityResponse,
            name='get_the_broken_servers',
            description='Вывод неработающих серверов'
            )
async def get_the_broken_servers(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objs, code, indexes = await crud_server.get_all_servers(db=session, skip=0, limit=LIMIT_SERVERS)
    servers_no_online = utils.check_server(objs)
    return ListOfEntityResponse(data=[getting_server(obj) for obj in servers_no_online])


# TODO: функция которая выдает все профили по сервер_айди
# @router.get(
#             path="/replacement/profiles/by/{server_id}/",
#             response_model=ListOfEntityResponse,
#             name='replacement_profiles_by_server_id',
#             description='Обновляет все профили по server_id'
#             )
# async def replacement_profiles_by_server_id(
#         server_id: int,
#         user: User = Depends(current_active_superuser),
#         session: AsyncSession = Depends(get_async_session),
# ):
#     profiles, code, indexes = await crud_profile.get_profiles_by_server_id(db=session, id=server_id)
#     await get_raise_new(code)
#
#     pass

if __name__ == "__main__":
    logging.info('Running...')
