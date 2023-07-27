import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from old_code.auth.base_config import fastapi_users
from old_code.auth.models import User
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from old_code.selling_point_type.crud import crud_selling_point_type as crud_sp_types
from old_code.selling_point_type.getters import getting_selling_point_type
from old_code.selling_point_type.schemas import SellingPointTypeCreate, SellingPointTypeUpdate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
current_active_user = fastapi_users.current_user(active=True)

router = APIRouter(
    prefix="/sp_type",
    tags=["SellingPointType"]
)


@router.get(
    path='/all',
    response_model=ListOfEntityResponse,
    name='get_sp_types',
    description='Получение списка типов точек сбыта'
)
async def get_sp_types(
        limit: int = 100,
        skip: int = 0,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    sp_types, code, indexes = await crud_sp_types.get_all_selling_point_types(db=session,
                                                                              skip=skip,
                                                                              limit=limit)
    return ListOfEntityResponse(data=[getting_selling_point_type(obj) for obj in sp_types])


@router.get(
    path="/{sp_type_id}",
    response_model=SingleEntityResponse,
    name='get_sp_type_by_id',
    description='Вывод типа точек сбыта по идентификатору'
)
async def get_sp_type_by_id(
        sp_type_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    sp_type, code, indexes = await crud_sp_types.get_selling_point_type_by_id(db=session,
                                                                              selling_point_type_id=sp_type_id)
    # ошибки обработать
    if code != 0:
        raise HTTPException(status_code=404, detail="Resource with this ID does not exist")
    return SingleEntityResponse(data=getting_selling_point_type(sp_type))


@router.post(
    path="/",
    response_model=SingleEntityResponse,
    name='create_sp_type',
    description='Добавление типа точек сбыта'
)
async def create_selling_point_type(
        new_data: SellingPointTypeCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    sp_type, code, indexes = await crud_sp_types.create_selling_point_type(db=session, new_data=new_data)
    if code != 0:
        raise HTTPException(status_code=409, detail="Resource already exists")
    return SingleEntityResponse(data=getting_selling_point_type(sp_type))


@router.put(
    path="/{sp_type_id}",
    response_model=SingleEntityResponse,
    name='update_sp_type',
    description='Изменить тип точек сбыта'
)
async def update_sp_type(
        update_data: SellingPointTypeUpdate,
        sp_type_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    sp_type, code, indexes = await crud_sp_types.update_selling_point_type(
        db=session,
        update_data=update_data,
        selling_point_type_id=sp_type_id
    )
    if code != 0:
        raise HTTPException(status_code=404, detail="Resource with this ID does not exist")
    return SingleEntityResponse(data=getting_selling_point_type(sp_type))


if __name__ == "__main__":
    logging.info('Running...')
