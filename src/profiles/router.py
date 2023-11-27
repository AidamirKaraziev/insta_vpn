import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import crud_account
from account.schemas import AccountUpdate
from config import LIMIT_PROFILES, TRIAL_DAYS

from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
from profiles.crud import crud_profile
from profiles.getters import getting_profile
from profiles.schemas import ProfileUpdate

from auth.base_config import fastapi_users
from auth.models import User
from referent.crud import crud_referent
from referent.schemas import ReferentCreate

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
        profile_id: UUID4,
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
    # создать профиль
    profile, code, indexes = await crud_profile.add_profile(db=session, account_id=account_id)
    await get_raise_new(code)
    """Добавление подарочных дней, если они есть у клиента"""
    account, code, indexes = await crud_account.get_account_by_id(db=session, id=account_id)
    await get_raise_new(code)
    if account.trial_is_active:
        date_end = (datetime.now().date() + timedelta(days=TRIAL_DAYS)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        activate_data = ProfileUpdate(date_end=date_end, is_active=True)
        profile, code, indexes = await crud_profile.activate_profile(db=session, id=profile.id,
                                                                     activate_data=activate_data)
        update_data = AccountUpdate(trial_is_active=False)
        account, code, indexes = await crud_account.update_account(db=session, id=account_id, update_data=update_data)
        await get_raise_new(code)
    return SingleEntityResponse(data=getting_profile(obj=profile))


@router.put(path="/activate/{profile_id}",
            response_model=SingleEntityResponse,
            name='activate_profile',
            description='Активировать профиль'
            )
async def activate_profile(
        activate_data: ProfileUpdate,
        profile_id: UUID4,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    # найти профиль
    profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
    obj, code, indexes = await crud_profile.activate_profile(db=session, activate_data=activate_data, id=profile_id)
    await get_raise_new(code)
    referent_data = ReferentCreate(telegram_id=profile.account_id)
    referent, code, indexes = await crud_referent.create_native_referent(db=session, new_data=referent_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_profile(obj=obj))


@router.put(path="/replacement-outline-key/{profile_id}",
            response_model=SingleEntityResponse,
            name='replacement_outline_key_for_profile',
            description='Заменить Outline ключ для профиля'
            )
async def replacement_outline_key_for_profile(
        profile_id: UUID4,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    profile, code, indexes = await crud_profile.replacement_outline_key_for_profile(db=session, profile_id=profile_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_profile(obj=profile))


@router.get(path="/deactivate-expired/",
            response_model=SingleEntityResponse,
            name='deactivate_expired_profile',
            description='Деактивирует активные профили, у которых истек срок действия'
            )
async def deactivate_expired_profile(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    date_of_disconnection = datetime.now()
    deactivate_profiles = []
    profiles, code, indexes = await crud_profile.get_profiles_by_date_end(
        db=session, your_date=date_of_disconnection)
    for profile in profiles:
        obj, code, indexes = await crud_profile.deactivate_profile(db=session, id=profile.id)
        deactivate_profiles.append(profile)
    await get_raise_new(code)
    return ListOfEntityResponse(data=[getting_profile(profile) for profile in deactivate_profiles])


@router.get(path="/counting-paid-profiles/{year_value}",
            response_model=ListOfEntityResponse,
            name='counting_paid_profiles',
            description='Подсчет оплаченных профилей'
            )
async def counting_paid_profiles(
        year_value: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    response = []
    data, code, indexes = await crud_profile.get_active_paid_profiles_per_month_in_year(db=session, year_value=year_value)
    for row in data:
        month = row.month
        active_count = row.active_count
        d = f"Месяц: {month}, Оплаченных профилей: {active_count}"
        response.append(d)
    return ListOfEntityResponse(data=[row for row in response])


@router.delete(path="/{profile_id}",
               response_model=SingleEntityResponse,
               name='delete_profile',
               description='Удалить профиль и все связанные с ним данные'
               )
async def delete_profile(
        profile_id: UUID4,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_profile.delete_profile(db=session, id=profile_id)
    await get_raise_new(code)
    return OkResponse()


if __name__ == "__main__":
    logging.info('Running...')
