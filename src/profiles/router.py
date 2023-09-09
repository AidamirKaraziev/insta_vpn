import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import FREE_TRAFFIC
from core.raise_template import get_raise
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from profiles.crud import crud_profile
from profiles.getters import getting_profile
from profiles.schemas import ProfileCreate, ProfileUpdate, ProfileActivate
from server.crud import crud_server
from utils.utils import update_data_in_profiles, outline_error

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
        # user: User = Depends(current_active_user),
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
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_profile(obj=obj))


@router.get(
            path="/by-account/{account_id}",
            response_model=ListOfEntityResponse,
            name='get_profiles_by_account_id',
            description='Вывод профиля по идентификатору'
            )
async def get_profiles_by_account_id(
        account_id: int,
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_profile.get_profiles_by_account_id(db=session, id=account_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in objects])


@router.post(path="/create/{account_id}",
             response_model=SingleEntityResponse,
             name='add_profile',
             description='Добавить профиль'
             )
async def add_profile(
        account_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    # выбрать сервер
    server, code, indexes = await crud_server.get_good_server(db=session)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    # проверка сколько у аккаунта пиров, дать имя пиру
    objects, code, indexes = await crud_profile.get_profiles_by_account_id(db=session, id=account_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    name = f"Профиль {len(objects) + 1}"
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
        # user: User = Depends(current_active_superuser),
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
        # user: User = Depends(current_active_superuser),
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
            path="/deactivate-account/",
            response_model=ListOfEntityResponse,
            name='deactivate_account',
            description='Деактивировать неоплаченные аккаунты'
            )
async def deactivate_account(
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_profile.deactivate_profile(db=session)
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
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await update_data_in_profiles(db=session, skip=0)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in objects])


if __name__ == "__main__":
    logging.info('Running...')
