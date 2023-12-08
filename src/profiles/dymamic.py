import logging
import re

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from database import get_async_session
from outline_key.crud import crud_outline_key
from profiles.crud import crud_profile
from profiles.schemas import ProfileUpdate
# пригодятся когда внедрим vless
# from starlette.responses import HTMLResponse
# import base64


router = APIRouter(
    tags=["DynamicKey"]
)


@router.get(
    path="/outline/{profile_id}",
    name='dynamic_connection_to_online_servers',
    description='Динамическое подключение к online серверам'
)
async def dynamic_connection_to_online_servers(
        profile_id: UUID4,
        session: AsyncSession = Depends(get_async_session),
):
    # Вернем профиль если такой есть
    profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
    # если профиль активен
    if profile.is_active is True:
        # если есть привязанный ключ
        if profile.outline_key_id is not None:
            outline_key, code, indexes = await crud_outline_key.get_key_by_id(db=session, id=profile.outline_key_id)
            await get_raise_new(code)
            # если привязанный ключ неактивен
            if outline_key.is_active is False:
                outline_key, code, indexes = await crud_outline_key.get_good_key_new(db=session)
                await get_raise_new(code)
                data = ProfileUpdate(outline_key_id=outline_key.id)
                profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)
                await get_raise_new(code)
        elif profile.outline_key_id is None:
            outline_key, code, indexes = await crud_outline_key.get_good_key_new(db=session)
            await get_raise_new(code)
            data = ProfileUpdate(outline_key_id=outline_key.id)
            profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)
            await get_raise_new(code)

        outline_key, code, indexes = await crud_outline_key.get_key_by_id(db=session, id=profile.outline_key_id)
        await get_raise_new(code)
        # Если привязанный ключ неактивен
        if outline_key.is_active is False:
            outline_key, code, indexes = await crud_outline_key.get_good_key_new(db=session)
            await get_raise_new(code)
            data = ProfileUpdate(outline_key_id=outline_key.id)
            profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)
            await get_raise_new(code)
    # ответ если профиль не активен
    elif profile.is_active is False:
        # TODO отправить смс в телегу
        await get_raise_new({"num": 403, "message": f"Подписка неактивна"})
    # Получаем
    outline_key, code, indexes = await crud_outline_key.get_key_by_id(db=session, id=profile.outline_key_id)
    await get_raise_new(code)
    access_url = re.findall(r'@(.*):', outline_key.access_url)
    res_for_app = {
        "server": f"{access_url[0]}",
        "server_port": f"{outline_key.port}",
        "password": f"{outline_key.password}",
        "method": f"{outline_key.method}"
    }
    return res_for_app


if __name__ == "__main__":
    logging.info('Running...')


# @router.get(
#     path="/outline/{profile_id}",
#     name='dynamic_connection_to_online_servers',
#     description='Динамическое подключение к online серверам'
# )
# async def dynamic_connection_to_online_servers(
#         profile_id: UUID4,
#         session: AsyncSession = Depends(get_async_session),
# ):
#     # Вернем профиль если такой есть
#     profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
#     await get_raise_new(code)
#     # если профиль активен
#     if profile.is_active is True:
#         # если есть привязанный ключ
#         if profile.outline_key_id is not None:
#             outline_key, code, indexes = await crud_outline_key.get_key_by_id(db=session, id=profile.outline_key_id)
#             await get_raise_new(code)
#             # если привязанный ключ неактивен
#             if outline_key.is_active is False:
#                 outline_key, code, indexes = await crud_outline_key.get_good_key(db=session)
#                 await get_raise_new(code)
#                 data = ProfileUpdate(outline_key_id=outline_key.id)
#                 profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)
#                 await get_raise_new(code)
#         elif profile.outline_key_id is None:
#             outline_key, code, indexes = await crud_outline_key.get_good_key(db=session)
#             await get_raise_new(code)
#             data = ProfileUpdate(outline_key_id=outline_key.id)
#             profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)
#             await get_raise_new(code)
#
#         outline_key, code, indexes = await crud_outline_key.get_key_by_id(db=session, id=profile.outline_key_id)
#         await get_raise_new(code)
#         # Если привязанный ключ неактивен
#         if outline_key.is_active is False:
#             outline_key, code, indexes = await crud_outline_key.get_good_key(db=session)
#             await get_raise_new(code)
#             data = ProfileUpdate(outline_key_id=outline_key.id)
#             profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)
#             await get_raise_new(code)
#     # ответ если профиль не активен
#     elif profile.is_active is False:
#         # TODO отправить смс в телегу
#         await get_raise_new({"num": 403, "message": f"Подписка неактивна"})
#     # Получаем
#     outline_key, code, indexes = await crud_outline_key.get_key_by_id(db=session, id=profile.outline_key_id)
#     await get_raise_new(code)
#     access_url = re.findall(r'@(.*):', outline_key.access_url)
#     res_for_app = {
#         "server": f"{access_url[0]}",
#         "server_port": f"{outline_key.port}",
#         "password": f"{outline_key.password}",
#         "method": f"{outline_key.method}"
#     }
#     return res_for_app

# @router.get(path="/conf/{profile_id}",
#             )
# async def encode_string(
#         profile_id: UUID4,
#         session: AsyncSession = Depends(get_async_session),
# ):
#     profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
#     await get_raise_new(code)
#     if profile.vpn_type_id == 1:  # SHADOWSOCKS
#         string = "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTpWRDFSeTZMdTZ6NVk0SThPUXlaOWM4@176.57.212.124:24705/?outline=1"
#         encoded_string = base64.b64encode(string.encode()).decode()
#         html_response = encoded_string
#         return HTMLResponse(html_response)
#     elif profile.vpn_type_id == 2:  # VLESS
#         string = "vless://a5397ed5-7479-4792-adc9-0fdb92c5cd90@176.57.212.124:443?type=tcp&security=reality&fp=firefox&pbk=n65lCyTgyOPYaRegNqxyfZfhBaGoP7JgLkXXQBnNvSw&sni=yahoo.com&sid=f8d8328e&spx=%2F#1-%D0%90%D0%B9%D0%B4%D0%B0%D0%BC%D0%B8%D1%80"
#         encoded_string = base64.b64encode(string.encode()).decode()
#         html_response = encoded_string
#         return HTMLResponse(html_response)
