import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import LIMIT_SERVERS
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
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


if __name__ == "__main__":
    logging.info('Running...')
