import logging
import re
import base64

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse

from core.raise_template import get_raise_new
from database import get_async_session
from profiles.crud import crud_profile
from profiles.schemas import ProfileUpdate
from shadowsocks_key.crud import crud_shadowsocks_key


router = APIRouter()


# TODO добавить #InstaVPN в урл, но он должен быть в нечитаемом формате, для красоты
@router.get(path="/conf/{profile_id}",
            )
async def encode_string(
        profile_id: UUID4,
        session: AsyncSession = Depends(get_async_session),
):
    # TODO продумать логику проверить работоспособность
    profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
    if profile.vpn_type_id == 1:  # SHADOWSOCKS
        string = "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTpWRDFSeTZMdTZ6NVk0SThPUXlaOWM4@176.57.212.124:24705/?outline=1"
        encoded_string = base64.b64encode(string.encode()).decode()
        html_response = encoded_string
        return HTMLResponse(html_response)
    elif profile.vpn_type_id == 2:  # VLESS
        string = "vless://a5397ed5-7479-4792-adc9-0fdb92c5cd90@176.57.212.124:443?type=tcp&security=reality&fp=firefox&pbk=n65lCyTgyOPYaRegNqxyfZfhBaGoP7JgLkXXQBnNvSw&sni=yahoo.com&sid=f8d8328e&spx=%2F#1-%D0%90%D0%B9%D0%B4%D0%B0%D0%BC%D0%B8%D1%80"
        encoded_string = base64.b64encode(string.encode()).decode()
        html_response = encoded_string
        return HTMLResponse(html_response)


# @router.get(path="/conf/{profile_id}",
#             )
# async def encode_string(
#         profile_id: UUID4,
#         session: AsyncSession = Depends(get_async_session),
# ):
#     # TODO продумать логику проверить работоспособность
#     profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
#     await get_raise_new(code)
#     if profile.vpn_type_id == 1:  # SHADOWSOCKS
#         if not profile.shadowsocks_key_id and profile.is_active:
#             shadowsocks_key, code, indexes = await crud_shadowsocks_key.get_good_key(db=session)
#             await get_raise_new(code)
#             data = ProfileUpdate(shadowsocks_key_id=shadowsocks_key.id)
#             profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)
#             # TODO сделать проверку если профиль не оплачен отправить в телеграм сообщение
#             shadowsocks_key, code, indexes = await crud_shadowsocks_key.get_shadowsocks_key_by_id(
#                 db=session, id=profile.shadowsocks_key_id)
#             if not shadowsocks_key.is_active:
#                 shadowsocks_key, code, indexes = await crud_shadowsocks_key.get_good_key(db=session)
#                 data = ProfileUpdate(shadowsocks_key_id=shadowsocks_key.id)
#                 profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)
#         shadowsocks_key, code, indexes = await crud_shadowsocks_key.get_shadowsocks_key_by_id(
#             db=session, id=profile.shadowsocks_key_id)
#         access_url = re.findall(r'@(.*):', shadowsocks_key.access_url)
#         res_for_app = {
#             "server": f"{access_url[0]}",
#             "server_port": f"{shadowsocks_key.port}",
#             "password": f"{shadowsocks_key.password}",
#             "method": f"{shadowsocks_key.method}"
#         }
#         return res_for_app
#     elif profile.vpn_type_id == 2:  # VLESS
#         string = "vless://a5397ed5-7479-4792-adc9-0fdb92c5cd90@176.57.212.124:443?type=tcp&security=reality&fp=firefox&pbk=n65lCyTgyOPYaRegNqxyfZfhBaGoP7JgLkXXQBnNvSw&sni=yahoo.com&sid=f8d8328e&spx=%2F#1-%D0%90%D0%B9%D0%B4%D0%B0%D0%BC%D0%B8%D1%80"
#         encoded_string = base64.b64encode(string.encode()).decode()
#         html_response = encoded_string
#         return HTMLResponse(html_response)


# http://127.0.0.1:8000/conf/003122d8-3dc6-4b37-89e4-612af7408c64


if __name__ == "__main__":
    logging.info('Running...')
