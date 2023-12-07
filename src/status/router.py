import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session

from auth.base_config import fastapi_users
from auth.models import User
from status.crud import crud_status
from status.getters import getting_status
from status.schemas import StatusCreate, StatusUpdate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/status",
    tags=["Status"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_statuses',
            description='Получение списка всех статусов'
            )
async def get_statuses(
        skip: int = 0,
        limit: int = 100,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_status.get_all_statuses(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_status(obj) for obj in objects])


@router.get(
            path="/{status_id}",
            response_model=SingleEntityResponse,
            name='get_status',
            description='Вывод статуса по id'
            )
async def get_status(
        status_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_status.get_status_by_id(db=session, id=status_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_status(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_status',
             description='Добавить новый статус'
             )
async def add_status(
        new_data: StatusCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_status.add_status(db=session, new_data=new_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_status(obj=obj))


@router.put(path="/{status_id}",
            response_model=SingleEntityResponse,
            name='update_status',
            description='Изменить данные статуса'
            )
async def update_status(
        update_data: StatusUpdate,
        status_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_status.update_status(db=session, update_data=update_data, id=status_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_status(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
