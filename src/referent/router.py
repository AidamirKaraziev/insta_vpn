import logging

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from auth.base_config import fastapi_users
from auth.models import User
from referent.crud import crud_referent
from referent.getters import getting_referent
from referent.schemas import ReferentCompanyCreate, ReferentNativeCreate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/referent",
    tags=["Referent"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_referents',
            description='Получение списка всех референтов'
            )
async def get_referents(
        skip: int = 0,
        limit: int = 1000,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_referent.get_all_referents(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_referent(obj) for obj in objects])


@router.get(
            path="/{referent_id}",
            response_model=SingleEntityResponse,
            name='get_referent',
            description='Вывод референта по идентификатору'
            )
async def get_referent(
        referent_id: UUID4,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_referent.get_referent_by_id(db=session, id=referent_id)
    await get_raise_new(code=code)
    return SingleEntityResponse(data=getting_referent(obj=obj))


# TODO возможно удалить, хз где это вообще применятся
@router.post(path="/create-native/",
             response_model=SingleEntityResponse,
             name='create_native_referent',
             description='Создает нативного референта(создается автоматически после регистрации в основном боте).'
             )
async def add_referent(
        new_data: ReferentNativeCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_referent.create_native_referent(db=session, new_data=new_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_referent(obj=obj))


@router.post(path="/create-for-us/",
             response_model=SingleEntityResponse,
             name='create_referent_for_us',
             description='Создать референта для нас, чтобы мы могли делать различные рекламные компании.'
             )
async def create_referent_for_us(
        new_data: ReferentCompanyCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_referent.create_referent_for_us(db=session, new_data=new_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_referent(obj=obj))


@router.get(
            path='/get-by/{telegram_id}',
            response_model=ListOfEntityResponse,
            name='get_referents_by_telegram_id',
            description='Получение списка референтов по телеграмм id '
            )
async def get_referents_by_telegram_id(
        telegram_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_referent.get_by_telegram_id(db=session, telegram_id=telegram_id)
    return ListOfEntityResponse(data=[getting_referent(obj) for obj in objects])


# TODO возможно потом удалить это апи потому что все будет происходить внутри кода
@router.get(
            path="/change-balance/{referent_id}",
            response_model=SingleEntityResponse,
            name='change_balance',
            description='Изменить баланс для референта'
            )
async def change_balance(
        referent_id: UUID4,
        amount: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_referent.change_balance(db=session, id=referent_id, amount=amount)
    await get_raise_new(code=code)
    return SingleEntityResponse(data=getting_referent(obj=obj))

# TODO select referents where is referent_type_id: int

if __name__ == "__main__":
    logging.info('Running...')
