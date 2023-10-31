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
            description='Подключение Outline '
            )
async def handle_payment(
        session: AsyncSession = Depends(get_async_session),
):
    res = """dmxlc3M6Ly85YzBiNTY4ZC00NDZhLTQwYzMtOTUxNC1iZjZlNzI0ZmVjOGFAMTc2LjU3LjIxMi4x
MjQ6NDQzP3R5cGU9dGNwJnNlY3VyaXR5PXJlYWxpdHkmZnA9ZmlyZWZveCZwYms9bjY1bEN5VGd5
T1BZYVJlZ05xeHlmWmZoQmFHb1A3SmdMa1hYUUJuTnZTdyZzbmk9eWFob28uY29tJmZsb3c9eHRs
cy1ycHJ4LXZpc2lvbiZzaWQ9ZjhkODMyOGUmc3B4PSUyRiMxLXRlc3Qy"""
    return res
