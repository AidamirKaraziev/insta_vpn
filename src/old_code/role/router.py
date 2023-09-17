import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import fastapi_users
from auth.models import User
from old_code.role.crud import crud_role
from old_code.role.getters import getting_role

from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session

current_active_user = fastapi_users.current_user(active=True)

router = APIRouter(
    prefix="/role",
    tags=["Role"]
)


@router.get(
            path="/all",
            response_model=ListOfEntityResponse,
            name='get_roles',
            description='Получение списка всех ролей'
            )
async def get_roles(
        skip: int = 0,
        limit: int = 100,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_role.get_all_role(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_role(obj) for obj in objects])


@router.get(
            path="/{role_id}",
            response_model=SingleEntityResponse,
            name="get_role",
            description='Вывод ролей по идентификатору'
            )
async def get_role(
        role_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_role.get_role_by_id(db=session, role_id=role_id)
    # ошибки обработать
    if code == -1:
        return SingleEntityResponse(data="ERROR")
    return SingleEntityResponse(data=getting_role(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
