import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import FREE_TRAFFIC, LIMIT_SERVERS
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
from profiles.getters import getting_profile
from server.crud import crud_server
from utils import utils


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
        session: AsyncSession = Depends(get_async_session),
):
    objs, code, indexes = await crud_server.get_all_servers(db=session, skip=0, limit=LIMIT_SERVERS)
    servers_no_online = utils.check_server(objs)
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in servers_no_online])


if __name__ == "__main__":
    logging.info('Running...')
