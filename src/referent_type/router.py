import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session

from auth.base_config import fastapi_users
from auth.models import User
from referent_type.crud import crud_referent_type
from referent_type.getters import getting_referent_type
from referent_type.schemas import ReferentTypeCreate, ReferentTypeUpdate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/referent_type",
    tags=["ReferentType"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_referent_types',
            description='Получение списка всех типов референтов'
            )
async def get_referent_types(
        skip: int = 0,
        limit: int = 100,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_referent_type.get_all_referent_types(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_referent_type(obj) for obj in objects])


@router.get(
            path="/{referent_type_id}",
            response_model=SingleEntityResponse,
            name='get_referent_type_id',
            description='Вывод типа референта по id'
            )
async def get_referent_type_id(
        referent_type_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_referent_type.get_referent_type_by_id(db=session, id=referent_type_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_referent_type(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_referent_type',
             description='Добавить новый тип референтов'
             )
async def add_referent_type(
        new_data: ReferentTypeCreate,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_referent_type.add_referent_type(db=session, new_data=new_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_referent_type(obj=obj))


@router.put(path="/{referent_type_id}",
            response_model=SingleEntityResponse,
            name='update_referent_type_id',
            description='Изменить данные типа референтов'
            )
async def update_referent_type_id(
        update_data: ReferentTypeUpdate,
        referent_type_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_referent_type.update_referent_type(db=session, update_data=update_data,
                                                                       id=referent_type_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_referent_type(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
