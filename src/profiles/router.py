import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from profiles.crud import crud_profile
from profiles.getters import getting_profile
from profiles.schemas import ProfileCreate, ProfileUpdate


# from old_code.auth.base_config import fastapi_users
# from old_code.auth.models import User
# current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
# current_active_user = fastapi_users.current_user(active=True)

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_profiles',
            description='Получение списка всех профилей'
            )
async def get_profiles(
        skip: int = 0,
        limit: int = 100,
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_profile.get_all_profiles(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_profile(obj) for obj in objects])


@router.get(
            path="/{profile_id}",
            response_model=SingleEntityResponse,
            name='get_profile',
            description='Вывод профиля по идентификатору'
            )
async def get_profile(
        profile_id: int,
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_profile(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_profile',
             description='Добавить профиль'
             )
async def add_profile(
        new_data: ProfileCreate,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    # выбрать свободный сервер -> ip_address.name
    # d = f"http://{ip_address.name}:51821/api/wireguard/client"
    obj, code, indexes = await crud_profile.add_profile(db=session, new_data=new_data)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_profile(obj=obj))


@router.put(path="/{profile_id}",
            response_model=SingleEntityResponse,
            name='update_profile',
            description='Изменить профиль'
            )
async def update_profile(
        update_data: ProfileUpdate,
        profile_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_profile.update_profile(db=session, update_data=update_data, id=profile_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_profile(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
