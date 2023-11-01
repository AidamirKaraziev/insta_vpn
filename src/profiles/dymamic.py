import re

from fastapi import APIRouter, Depends
from fastapi import FastAPI, UploadFile, File, Response
from pydantic import UUID4
from requests import request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse

from core.raise_template import get_raise_new
from database import get_async_session
from profiles.crud import crud_profile
from profiles.schemas import ProfileUpdate
from static_key.crud import crud_static_key
import base64

router = APIRouter()


@router.get("/encode",
            response_class=HTMLResponse)
def encode_string(response: Response):
    string = "vless://a5397ed5-7479-4792-adc9-0fdb92c5cd90@176.57.212.124:443?type=tcp&security=reality&fp=firefox&pbk=n65lCyTgyOPYaRegNqxyfZfhBaGoP7JgLkXXQBnNvSw&sni=yahoo.com&sid=f8d8328e&spx=%2F#1-%D0%90%D0%B9%D0%B4%D0%B0%D0%BC%D0%B8%D1%80"
    encoded_string = base64.b64encode(string.encode()).decode()

    # Установите заголовок Content-Type на text/html
    # response.headers["Content-Type"] = "text/html"

    # Сформируйте ответ в виде HTML строки
    html_response = encoded_string
    return html_response


@router.get(path='/conf/{profile_id}',
            name='outline_connect',
            description='Подключение Outline ',
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


def encode_to_base64(str):
    encoded_bytes = base64.b64encode(str.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')
    return encoded_str


@router.get(path='/test-vless/',
            name='outline_connect',
            description='Подключение Outline'
            )
async def handle_payment(
        session: AsyncSession = Depends(get_async_session),
):
    my_string = "vless://9c0b568d-446a-40c3-9514-bf6e724fec8a@176.57.212.124:443?type=tcp&security=reality&fp=firefox&pbk=n65lCyTgyOPYaRegNqxyfZfhBaGoP7JgLkXXQBnNvSw&sni=yahoo.com&flow=xtls-rprx-vision&sid=f8d8328e&spx=%2F#1-test2"
    encoded_string = encode_to_base64(my_string)
    print(encoded_string)

    return encoded_string

