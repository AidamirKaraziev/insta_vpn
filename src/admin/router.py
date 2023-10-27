import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new, raise_schemas
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session
from server.crud import crud_server
from server.getters import getting_server
from server.schemas import ServerCreate
from static_key.crud import crud_static_key
from auth.base_config import fastapi_users
from auth.models import User

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# здесь будут все администраторские апи
@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_server_create_keys',
             description='Добавить сервер и создать ключи для него'
             )
async def add_server_create_keys(
        new_data: ServerCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    try:
        server, code, indexes = await crud_server.add_server(db=session, new_data=new_data)
        await get_raise_new(code)
        keys, code, indexes = await crud_static_key.creating_keys_for_a_server(db=session, server_id=server.id)
        await get_raise_new(code)
        return SingleEntityResponse(data=getting_server(obj=server))
    except Exception as ex:
        await get_raise_new(raise_schemas(ex))


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

