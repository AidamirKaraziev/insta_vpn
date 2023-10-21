import re

from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from database import get_async_session
from profiles.crud import crud_profile
from config import OUTLINE_SALT
from profiles.schemas import ProfileUpdate
from static_key.crud import crud_static_key

router = APIRouter()


@router.get(path='/conf/{hex_id}',
            name='outline_connect',
            description='Подключение Outline '
            )
async def handle_payment(
        hex_id: str,
        session: AsyncSession = Depends(get_async_session),
):
    f = Fernet(OUTLINE_SALT)
    profile_id = f.decrypt(bytes(hex_id.encode()))
    profile_id = int(profile_id.decode())

    profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
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
