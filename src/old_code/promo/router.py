import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import fastapi_users
from auth.models import User
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from old_code.promo.crud import crud_promo
from old_code.promo.getters import getting_promo
from old_code.promo.schemas import PromoUpdate, PromoCreate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
current_active_user = fastapi_users.current_user(active=True)

router = APIRouter(
    prefix="/promo",
    tags=["Promo"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_promos',
            description='Получение списка всех рекламируемых групп'
            )
async def get_promos(
        skip: int = 0,
        limit: int = 100,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_promo.get_all_promo(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_promo(obj) for obj in objects])


@router.get(
            path="/{promo_id}",
            response_model=SingleEntityResponse,
            name='get_promo',
            description='Вывод рекламируемой группы по идентификатору'
            )
async def get_promo(
        promo_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_promo.get_promo_by_id(db=session, promo_id=promo_id)
    if code != 0:
        return SingleEntityResponse(data=f"ERROR: {code}")
    return SingleEntityResponse(data=getting_promo(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='create_promo',
             description='Создать рекламируемую группу'
             )
async def create_promo(
        new_data: PromoCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_promo.create_promo(db=session, new_data=new_data)
    if code != 0:
        return SingleEntityResponse(data=f"ERROR: {code}")
    return SingleEntityResponse(data=getting_promo(obj=obj))


@router.put(path="/{promo_id}",
            response_model=SingleEntityResponse,
            name='update_promo',
            description='Изменить рекламируемую группу'
            )
async def update_promo(
        update_data: PromoUpdate,
        promo_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_promo.update_promo(db=session,
                                                       update_data=update_data,
                                                       promo_id=promo_id)
    if code != 0:
        raise HTTPException(status_code=400, detail=code)
    return SingleEntityResponse(data=getting_promo(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
