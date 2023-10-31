import re

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from database import get_async_session
from profiles.crud import crud_profile
from profiles.schemas import ProfileUpdate
from static_key.crud import crud_static_key

router = APIRouter()


@router.get(path='/conf/{profile_id}',
            name='outline_connect',
            description='Подключение Outline '
            )
async def handle_payment(
        profile_id: UUID4,
        session: AsyncSession = Depends(get_async_session),
):
    profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
    # TODO сделать проверку если профиль не оплачен отправить в телеграм сообщение
    if not profile.static_key_id and profile.is_active:
        static_key, code, indexes = await crud_static_key.get_good_key(db=session)
        data = ProfileUpdate(static_key_id=static_key.id)
        profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)

    static_key, code, indexes = await crud_static_key.get_static_key_by_id(db=session, id=profile.static_key_id)
    if not static_key.is_active:
        static_key, code, indexes = await crud_static_key.get_good_key(db=session)
        data = ProfileUpdate(static_key_id=static_key.id)
        profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)
    access_url = re.findall(r'@(.*):', static_key.access_url)
    res_for_app = {
        "server": f"{access_url[0]}",
        "server_port": f"{static_key.port}",
        "password": f"{static_key.password}",
        "method": f"{static_key.method}"
    }
    return res_for_app



"""TEST dynamic key VLESS"""


@router.get(path='/test-vless/',
            name='outline_connect',
            description='Подключение Outline'
            )
async def handle_payment(
        session: AsyncSession = Depends(get_async_session),
):
    res = "vless://9c0b568d-446a-40c3-9514-bf6e724fec8a@176.57.212.124:443?type=tcp&security=reality&fp=firefox&pbk=n65lCyTgyOPYaRegNqxyfZfhBaGoP7JgLkXXQBnNvSw&sni=yahoo.com&flow=xtls-rprx-vision&sid=f8d8328e&spx=%2F#1-test2"
    return res
