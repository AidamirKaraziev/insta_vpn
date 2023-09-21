import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import FREE_TRAFFIC
from core.raise_template import get_raise, get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from profiles.crud import crud_profile
from profiles.getters import getting_profile
from profiles.schemas import ProfileCreate, ProfileUpdate, ProfileActivate
from server.crud import crud_server
from utils.utils import update_used_bytes_in_profiles, outline_error, deactivate_profile, deleting_an_outdated_profile
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
        skip: int = 0,
        limit: int = 100,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_profile.get_all_profiles(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in objects])


@router.get(
            path="/{profile_id}",
            response_model=SingleEntityResponse,
            name='get_profile',
            description='Вывод профиля по идентификатору'
            )
async def get_profile(
        profile_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_profile(obj=obj))


@router.get(
            path="/by-account/{account_id}",
            response_model=ListOfEntityResponse,
            name='get_profiles_by_account_id',
            description='Вывод профиля по идентификатору'
            )
async def get_profiles_by_account_id(
        account_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_profile.get_profiles_by_account_id(db=session, id=account_id)
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
    try:
        # создать пир
        client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
        new_key = client.create_key()
        client.add_data_limit(key_id=new_key.key_id, limit_bytes=FREE_TRAFFIC)
    except Exception as ex:
        return None, outline_error(ex), None
    # сделать запись в базу данных
    profile = ProfileCreate(account_id=account_id, server_id=server.id, key_id=new_key.key_id, name=name,
                            port=new_key.port, method=new_key.method, access_url=new_key.access_url,
                            used_bytes=new_key.used_bytes, data_limit=FREE_TRAFFIC)
    profile, code, indexes = await crud_profile.add_profile(db=session, new_data=profile)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_profile(obj=profile))


@router.put(path="/activate/{profile_id}/",
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
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    # найти сервер
    server, code, indexes = await crud_server.get_server_by_id(db=session, id=profile.server_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
    try:
        client.delete_data_limit(key_id=profile.key_id)
    except Exception as ex:
        return f"Не получилось снять ограничение потому что: {ex}"

    obj, code, indexes = await crud_profile.activate_profile(db=session, activate_data=activate_data, id=profile_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
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
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    # найти сервер
    server, code, indexes = await crud_server.get_server_by_id(db=session, id=profile.server_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
    try:
        client.delete_key(key_id=profile.key_id)
    except Exception as ex:
        return f"не получилось удалить ключ потому что: {ex}"

    obj, code, indexes = await crud_profile.delete_profile(db=session, id=profile_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return OkResponse()


@router.get(
            path="/deactivate-old/",
            response_model=ListOfEntityResponse,
            name='deactivate_old_profiles',
            description='Деактивировать неоплаченные профили'
            )
async def deactivate_old_profiles(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await deactivate_profile(db=session)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in objects])


@router.get(
            path="/used-bytes/",
            response_model=ListOfEntityResponse,
            name='update_used_bytes_in_profile',
            description='Обновить used_bytes во всех профилях'
            )
async def update_used_bytes_in_profile(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await update_used_bytes_in_profiles(db=session, skip=0)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in objects])


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
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
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

    client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
    try:
        client.delete_key(key_id=profile.key_id)
    except Exception as ex:
        return f"не получилось удалить ключ потому что: {ex}"
    # создание нового ключа
    new_server, code, indexes = await crud_server.get_good_server(db=session)
    await get_raise_new(code)
    # присвоение профилю новых данных
    try:
        client = OutlineVPN(api_url=new_server.api_url, cert_sha256=new_server.cert_sha256)
        new_key = client.create_key()
    except Exception as ex:
        return None, outline_error(ex), None
    # сделать запись в базу данных
    update_data = ProfileUpdate(key_id=new_key.key_id, port=new_key.port, method=new_key.method,
                                access_url=new_key.access_url, used_bytes=new_key.used_bytes, data_limit=0)
    profile, code, indexes = await crud_profile.update_profile(db=session, update_data=update_data, id=profile.id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_profile(obj=profile))


if __name__ == "__main__":
    logging.info('Running...')
