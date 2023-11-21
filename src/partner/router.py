import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session

from auth.base_config import fastapi_users
from auth.models import User
from partner.crud import crud_partner
from partner.getters import getting_partner
from partner.schemas import PartnerCreate, PartnerUpdate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/partner",
    tags=["Partner"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_partners',
            description='Получение списка всех партнеров'
            )
async def get_partners(
        skip: int = 0,
        limit: int = 100,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_partner.get_all_partners(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_partner(obj) for obj in objects])


@router.get(
            path="/{partner_id}",
            response_model=SingleEntityResponse,
            name='get_partner',
            description='Вывод партнера по идентификатору'
            )
async def get_partner(
        partner_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_partner.get_partner_by_id(db=session, id=partner_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_partner(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_partner',
             description='Добавить нового партнера'
             )
async def add_partner(
        new_data: PartnerCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_partner.add_partner(db=session, new_data=new_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_partner(obj=obj))


@router.put(path="/{partner_id}",
            response_model=SingleEntityResponse,
            name='update_partner',
            description='Изменить данные партнера'
            )
async def update_partner(
        update_data: PartnerUpdate,
        partner_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_partner.update_partner(db=session, update_data=update_data, id=partner_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_partner(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
