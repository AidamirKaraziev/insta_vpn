import re

from fastapi import APIRouter, Depends, HTTPException, FastAPI
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from profiles.crud import crud_profile
from config import OUTLINE_USERS_GATEWAY, OUTLINE_SALT, CONN_NAME

router = APIRouter()


@router.get(path='/conf/%s{hex_id}' % OUTLINE_SALT,
            name='outline_connect',
            description='Подключение Outline '
            )
async def handle_payment(
        hex_id: str,
        session: AsyncSession = Depends(get_async_session),
):
    profile_id = int(hex_id, 0)
    response, code, indexes = await crud_profile.get_config_by_id(db=session, profile_id=profile_id)
    access_url = re.findall(r'@(.*):', response.access_url)
    d = {
        "server": f"{access_url[0]}",
        "server_port": f"{response.port}",
        "password": f"{response.password}",
        "method": f"{response.method}"
    }
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    print(d)
    return Response(content='ssconf://95.182.120.204:55713/conf/qwerty1230x13#Wow!', media_type='text/plain')


def gen_outline_dynamic_link(profile_id: int):
    print(hex(profile_id))
    return f"{OUTLINE_USERS_GATEWAY}/conf/{OUTLINE_SALT}{hex(profile_id)}#{CONN_NAME}"

