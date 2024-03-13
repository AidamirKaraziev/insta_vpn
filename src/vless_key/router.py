import logging
import requests

from fastapi import APIRouter, Depends, Body, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
from auth.base_config import fastapi_users
from auth.models import User
from vless_key.crud import crud_vless_key
from vless_key.getters import getting_vless_key
from vless_key.shcemas import VlessKeyCreate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/vless_key",
    tags=["VlessKey"]
)


async def authorization():
    """
    Авторизация в
    """
    pass

"""
Бро будем авторизовываться по одному адресу или будем менять адрес для каждого vless сервера 
https://vless.insta-vpn.ru/api/admin/token

"""


@router.get("/auth")
def get_user_info():
    token_url = "https://vless.insta-vpn.ru/api/admin/token"
    token_payload = {
        "grant_type": "",
        "username": "karaziev",
        "password": "2432546Mb",
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }
    token_response = requests.post(token_url, data=token_payload)
    if token_response.status_code == 200:
        access_token = token_response.json()["access_token"]
        user_info_url = "https://vless.insta-vpn.ru/api/user/Aidamir"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        user_info_response = requests.get(user_info_url, headers=headers)
        return user_info_response.json()

    else:
        return {"error": "Failed to obtain access token"}


@router.get("/profile/{profile_name}")
def get_user_info(
        profile_name: str = 'Aidamir',
):
    # TODO авторизоваться
    token_url = "https://vless.insta-vpn.ru/api/admin/token"

    token_payload = {
        "grant_type": "",
        "username": "karaziev",
        "password": "2432546Mb",
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }
    response = requests.post(token_url, data=token_payload)
    url = f"https://vless.insta-vpn.ru/api/user/{profile_name}"
    print(response)
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJrYXJhemlldiIsImFjY2VzcyI6InN1ZG8iLCJpYXQiOjE3MDgxNzg2ODMsImV4cCI6MTcwODI2NTA4M30.yQseDjf6PGtx-pzyoDxRPh6j2tvjYSEj0FDf3QBskGc"
    }
    response = requests.get(token_url, headers=headers)
    return response.json()


@router.get(
            path='/connect-to-server',
            # response_model=ListOfEntityResponse,
            name='connect_to_server',
            description='Подключение к серверу с получением данных пользователя по имени'
            )
async def connect_to_server(
        username: str,
        # limit: int = 1000,
        # user: User = Depends(current_active_superuser),
        # session: AsyncSession = Depends(get_async_session),
):

    return "OK"
    # objects, code, indexes = await crud_vless_key.get_all_vless_keys(db=session, skip=0, limit=limit)
    # return ListOfEntityResponse(data=[getting_vless_key(obj) for obj in objects])


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_vless_key',
            description='Получение списка всех ключей'
            )
async def get_vless_key(
        limit: int = 1000,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_vless_key.get_all_vless_keys(db=session, skip=0, limit=limit)
    return ListOfEntityResponse(data=[getting_vless_key(obj) for obj in objects])


@router.get(
            path="/{vless_key_id}",
            response_model=SingleEntityResponse,
            name='get_vless_key',
            description='Вывод ключа по идентификатору'
            )
async def get_vless_key(
        vless_key_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_vless_key.get_vless_key_by_id(db=session, id=vless_key_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_vless_key(obj=obj))


@router.get(
            path="/by/{server_ip}",
            response_model=ListOfEntityResponse,
            name='get_vless_keys_by_server_ip',
            description='Вывод статических ключей по ip сервера'
            )
async def get_vless_keys_by_server_ip(
        server_ip: str,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_vless_key.get_vless_keys_by_server_ip(db=session, server_ip=server_ip)
    await get_raise_new(code)
    return ListOfEntityResponse(data=[getting_vless_key(obj) for obj in objects])


def extract_urls(text):
    urls = text.split('\n')
    return urls


@router.post(path="/create-many/{server_ip}",
             response_model=SingleEntityResponse,
             name='add_vless_keys',
             description='Добавить ключи'
             )
async def add_vless_keys(
        server_ip: str,
        file: UploadFile = File(...),

        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    file_content = await file.read()
    list_link = file_content.decode().split('\r\n')
    objects, code, indexes = await crud_vless_key.create_many_keys_with_server_ip(
        db=session, server_ip=server_ip, list_link=list_link)
    await get_raise_new(code)
    return SingleEntityResponse(data=objects)


@router.post(path="/create/",
             response_model=SingleEntityResponse,
             name='add_vless_key',
             description='Добавить ключ'
             )
async def add_vless_key(
        new_data: VlessKeyCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    key, code, indexes = await crud_vless_key.create_key(db=session, new_data=new_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_vless_key(obj=key))


@router.get(path="/deactivate/{server_ip}",
            response_model=ListOfEntityResponse,
            name='deactivate_vless_keys_by_server_ip',
            description='Деактивация VLESS ключей по server_ip'
            )
async def deactivate_vless_keys_by_server_ip(
        server_ip: str,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    keys, code, indexes = await crud_vless_key.deactivate_keys_by_server_ip(db=session, server_ip=server_ip)
    await get_raise_new(code)
    return ListOfEntityResponse(data=[getting_vless_key(obj) for obj in keys])


@router.get(path="/activate/{server_ip}",
            response_model=ListOfEntityResponse,
            name='deactivate_vless_keys_by_server_ip',
            description='Деактивация VLESS ключей по server_ip'
            )
async def deactivate_vless_keys_by_server_ip(
        server_ip: str,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    keys, code, indexes = await crud_vless_key.activate_keys_by_server_ip(db=session, server_ip=server_ip)
    await get_raise_new(code)
    return ListOfEntityResponse(data=[getting_vless_key(obj) for obj in keys])


@router.delete(path="/{server_ip}",
               response_model=SingleEntityResponse,
               name='delete_keys_by_server_ip',
               description='Удалить ключи по server_ip'
               )
async def delete_keys_by_server_ip(
        server_ip: str,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    datum, code, indexes = await crud_vless_key.delete_keys_by_server_ip(db=session, server_ip=server_ip)
    await get_raise_new(code)
    return SingleEntityResponse(data=datum)


if __name__ == "__main__":
    logging.info('Running...')

# @router.get(path="/free-keys-output/",
#             response_model=SingleEntityResponse,
#             name='output_how_many_free_keys',
#             description='Вывести сколько есть свободных ключей'
#             )
# async def output_how_many_free_keys(
#         # user: User = Depends(current_active_superuser),
#         session: AsyncSession = Depends(get_async_session),
# ):
#     quantity_free_keys, code, indexes = await crud_vless_key.get_quantity_free_keys(db=session)
#     await get_raise_new(code)
#     response = f"Свободных ключей: {quantity_free_keys}"
#     return SingleEntityResponse(data=response)

# TODO отложенная задача, которая отправляет уведомление если количество хороших ключей опускается до 100 шт
# TODO delete by id
# TODO deactivate by id
