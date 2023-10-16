import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import FREE_TRAFFIC, LIMIT_PROFILES, OUTLINE_SALT
from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from profiles.crud import crud_profile
from profiles.dymamic import gen_outline_dynamic_link
from profiles.getters import getting_profile
from profiles.schemas import ProfileCreate, ProfileUpdate, ProfileActivate
from server.crud import crud_server
from utils.utils import update_used_bytes_in_profiles, outline_error, deleting_an_outdated_profile, deactivate_profile, \
    get_keys_without_a_profile_and_bad_server
from auth.base_config import fastapi_users
from auth.models import User

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_profiles',
            description='Получение списка всех профилей'
            )
async def get_profiles(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_profile.get_all_profiles(db=session, skip=0, limit=LIMIT_PROFILES)
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in objects])


@router.get(
            path="/{profile_id}",
            response_model=SingleEntityResponse,
            name='get_profile',
            description='Вывод профиля по идентификатору'
            )
async def get_profile(
        profile_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_profile(obj=obj))


@router.get(
            path="/by-account/{account_id}",
            response_model=ListOfEntityResponse,
            name='get_profiles_by_account_id',
            description='Вывод профиля по аккаунт идентификатору'
            )
async def get_profiles_by_account_id(
        account_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_profile.get_profiles_by_account_id(db=session, id=account_id)
    await get_raise_new(code)
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in objects])


@router.get(
            path="/by-server/{server_id}",
            response_model=ListOfEntityResponse,
            name='get_profiles_by_server_id',
            description='Вывод профиля по сервер идентификатору'
            )
async def get_profiles_by_server_id(
        server_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_profile.get_profiles_by_server_id(db=session, id=server_id)
    await get_raise_new(code)
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in objects])


@router.post(path="/create/{account_id}",
             response_model=SingleEntityResponse,
             name='add_profile',
             description='Добавить профиль'
             )
async def add_profile(
        account_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    # выбрать сервер
    server, code, indexes = await crud_server.get_good_server(db=session)
    await get_raise_new(code)
    # проверка сколько у аккаунта пиров, дать имя пиру
    objects, code, indexes = await crud_profile.get_profiles_by_account_id(db=session, id=account_id)
    await get_raise_new(code)
    # получение имени для профиля
    name, code, indexes = await crud_profile.get_name_for_profile(db=session, account_id=account_id)
    await get_raise_new(code)

    client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
    # TODO: попросить азамата сделать ревью кода
    # создание профиля
    data_profile = ProfileCreate(account_id=account_id, server_id=server.id, name=name)
    profile, code, indexes = await crud_profile.add_profile(db=session, new_data=data_profile)
    # создание ключа
    try:
        new_key = client.create_key()
        try:
            client.add_data_limit(key_id=new_key.key_id, limit_bytes=FREE_TRAFFIC)
        except Exception as ex:
            await get_raise_new(code=outline_error(ex))
    except Exception as ex:
        await get_raise_new(code=outline_error(ex))
    # генерация ключа
    dynamic_key = gen_outline_dynamic_link(profile_id=profile.id)
    # обновление в профиль
    update_profile = ProfileUpdate(key_id=new_key.key_id, port=new_key.port, password=new_key.password,
                                   method=new_key.method, access_url=new_key.access_url, used_bytes=new_key.used_bytes,
                                   data_limit=FREE_TRAFFIC, dynamic_key=dynamic_key)
    profile, code, indexes = await crud_profile.update_profile(db=session, id=profile.id, update_data=update_profile)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_profile(obj=profile))


@router.put(path="/activate/{profile_id}",
            response_model=SingleEntityResponse,
            name='activate_profile',
            description='Активировать профиль'
            )
async def activate_profile(
        activate_data: ProfileActivate,
        profile_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    # найти профиль
    profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
    # найти сервер
    server, code, indexes = await crud_server.get_server_by_id(db=session, id=profile.server_id)
    await get_raise_new(code)
    try:
        client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
        client.delete_data_limit(key_id=profile.key_id)
    except Exception as ex:
        return f"Не получилось снять ограничение потому что: {ex}"
    obj, code, indexes = await crud_profile.activate_profile(db=session, activate_data=activate_data, id=profile_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_profile(obj=obj))


@router.delete(path="/{profile_id}",
               response_model=SingleEntityResponse,
               name='delete_profile',
               description='Удалить профиль'
               )
async def delete_profile(
        profile_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    # проверить профиль
    profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
    # найти сервер
    server, code, indexes = await crud_server.get_server_by_id(db=session, id=profile.server_id)
    await get_raise_new(code)
    try:
        client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
        client.delete_key(key_id=profile.key_id)
    except Exception as ex:
        return f"не получилось удалить ключ потому что: {ex}"

    obj, code, indexes = await crud_profile.delete_profile(db=session, id=profile_id)
    await get_raise_new(code)
    return OkResponse()


@router.get(
            path="/deactivate-old/",
            response_model=SingleEntityResponse,
            name='deactivate_old_profiles',
            description='Деактивировать неоплаченные профили'
            )
async def deactivate_old_profiles(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await deactivate_profile(db=session)
    await get_raise_new(code)
    return SingleEntityResponse(data=objects)


@router.get(
            path="/used-bytes/",
            response_model=OkResponse,
            name='update_used_bytes_in_profile',
            description='Обновить used_bytes во всех профилях возвращает '
            )
async def update_used_bytes_in_profile(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await update_used_bytes_in_profiles(db=session, skip=0)
    await get_raise_new(code)
    return OkResponse()


@router.get(
            path="/get-keys-without-a-profile/",
            response_model=ListOfEntityResponse,
            name='get_keys_without_a_profile',
            description='Получить ключи без профиля'
            )
async def get_keys_without_a_profile(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await get_keys_without_a_profile_and_bad_server(db=session, skip=0)
    await get_raise_new(code)
    return ListOfEntityResponse(data=objects)


# delete old profiles
@router.get(
            path="/delete-old/",
            response_model=SingleEntityResponse,
            name='delete_old',
            description='Удалить устаревшие профили!'
            )
async def delete_old(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await deleting_an_outdated_profile(db=session)
    await get_raise_new(code)
    return SingleEntityResponse(data=obj)


@router.put(path="/replacement/{profile_id}",
            response_model=SingleEntityResponse,
            name='replacement_profile',
            description='Заменить ключ для профиля'
            )
async def replacement_profile(
        profile_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    # проверить профиль
    profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
    # найти сервер
    server, code, indexes = await crud_server.get_server_by_id(db=session, id=profile.server_id)
    await get_raise_new(code)
    replacement_server, code, indexes = await crud_server.get_replacement_server(
        db=session, server_id=profile.server_id)
    await get_raise_new(code)
    client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
    try:
        client.delete_key(key_id=profile.key_id)
    except Exception as ex:
        return f"не получилось удалить ключ потому что: {ex}"
    try:
        client = OutlineVPN(api_url=replacement_server.api_url, cert_sha256=replacement_server.cert_sha256)
        new_key = client.create_key()
    except Exception as ex:
        return None, outline_error(ex), None
    # сделать запись в базу данных
    update_data = ProfileUpdate(server_id=replacement_server.id, key_id=new_key.key_id, port=new_key.port,
                                method=new_key.method, access_url=new_key.access_url, used_bytes=new_key.used_bytes,
                                data_limit=0)
    profile, code, indexes = await crud_profile.update_profile(db=session, update_data=update_data, id=profile.id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_profile(obj=profile))


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
    print(d)
    return d
if __name__ == "__main__":
    logging.info('Running...')
