import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import crud_account
from account.getters import getting_account
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from auth.base_config import fastapi_users
from auth.models import User
from profiles.crud import crud_profile
from sqlite3 import Timestamp

from profiles.getters import getting_profile

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get(
            path='/get-profiles-by-filter/ ',
            response_model=ListOfEntityResponse,
            name='get_profiles_by_filter',
            description='Получение списка профилей отфильтрованных по дате окончания и активности:"2023-11-20T19:28:13"'
            )
async def get_profiles_by_filter(
        date_end_min: Timestamp,
        date_end_max: Timestamp,
        is_active: Optional[bool] = None,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_profile.get_profiles_by_filter(
        db=session, date_end_min=date_end_min, date_end_max=date_end_max, is_active=is_active)
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in objects])


@router.get(
            path='/get-accounts-without-profile/',
            response_model=ListOfEntityResponse,
            name='get_accounts_without_profile',
            description='Список аккаунтов без профиля'
            )
async def get_accounts_without_profile(
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session)
):
    objects, code, indexes = await crud_account.get_accounts_without_profile(db=session)
    return ListOfEntityResponse(data=[getting_account(obj) for obj in objects])


if __name__ == "__main__":
    logging.info('Running...')

"""ВАЖНО"""
# TODO У нас изменился profile_id. квитанции оплаты привязаны к этим ID. Что будет если тормоза решатся оплатить?)))
#  можно ли очистить диалог у тормозов?
#  возможно дописать код, чтобы проходила проверка на "тормоза"?


"""Функционал который требует обсуждения"""
# TODO сделать одну почту для всех созданных серверов
# TODO Можем ли мы получить инфу когда человек отключается от впн в приложении???(Нажатие кнопки)


"""Celery"""
# TODO отключение неоплаченных профилей -> смс клиенту
# TODO CELERY сделать рассылку сообщений пользователям


"""Реферальная программа"""


"""Утвержденные задачи -> перенести в Notion"""
# TODO добавить комментарии к каждой функции и методу
# TODO регистрация - бесплатный период, код с настройками - оплата - реферальная программа
# TODO написать диагностику впн серверов. сделать это отдельно
# TODO автоматические выплаты
# TODO сделать вывод у кого

# TODO добавить в referent поля balance, spb_number
# TODO добавить в account поле can_pay_out: True написать логику выплаты пользователям и проставления can_pay_out: False
# TODO сделать вывод баланса
# TODO удалить директорию static
