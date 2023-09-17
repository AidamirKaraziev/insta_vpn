import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from tariff.crud import crud_tariff
from tariff.getters import getting_tariff
from tariff.schemas import TariffCreate, TariffUpdate
from auth.base_config import fastapi_users
from auth.models import User

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/tariff",
    tags=["Tariff"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_tariffs',
            description='Получение списка всех тарифов'
            )
async def get_tariffs(
        skip: int = 0,
        limit: int = 100,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_tariff.get_all_tariffs(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_tariff(obj) for obj in objects])


@router.get(
            path="/{tariff_id}",
            response_model=SingleEntityResponse,
            name='get_tariff',
            description='Вывод тарифа по идентификатору'
            )
async def get_tariff(
        tariff_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_tariff.get_tariff_by_id(db=session, id=tariff_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_tariff(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_tariff',
             description='Добавить тариф'
             )
async def add_tariff(
        new_data: TariffCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_tariff.add_tariff(db=session, new_data=new_data)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_tariff(obj=obj))


@router.put(path="/{tariff_id}",
            response_model=SingleEntityResponse,
            name='update_tariff',
            description='Изменить тариф'
            )
async def update_tariff(
        update_data: TariffUpdate,
        tariff_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_tariff.update_tariff(db=session, update_data=update_data, id=tariff_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_tariff(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
