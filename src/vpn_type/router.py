import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise, get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session

from auth.base_config import fastapi_users
from auth.models import User
from vpn_type.crud import crud_vpn_type
from vpn_type.getters import getting_vpn_type
from vpn_type.schemas import VpnTypeCreate, VpnTypeUpdate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/vpn_type",
    tags=["VpnType"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_vpn_types',
            description='Получение списка всех VPN типов '
            )
async def get_vpn_types(
        skip: int = 0,
        limit: int = 100,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_vpn_type.get_all_vpn_types(db=session, skip=skip, limit=limit)
    print(objects)
    return ListOfEntityResponse(data=[getting_vpn_type(obj) for obj in objects])


@router.get(
            path="/{vpn_type_id}",
            response_model=SingleEntityResponse,
            name='get_vpn_type',
            description='Вывод VPN типа по идентификатору'
            )
async def get_vpn_type(
        vpn_type_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_vpn_type.get_vpn_type_by_id(db=session, id=vpn_type_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_vpn_type(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_vpn_type',
             description='Добавить новый VPN тип'
             )
async def add_vpn_type(
        new_data: VpnTypeCreate,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_vpn_type.add_vpn_type(db=session, new_data=new_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_vpn_type(obj=obj))


@router.put(path="/{vpn_type_id}",
            response_model=SingleEntityResponse,
            name='update_vpn_type',
            description='Изменить VPN тип'
            )
async def update_vpn_type(
        update_data: VpnTypeUpdate,
        vpn_type_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_vpn_type.update_vpn_type(db=session, update_data=update_data, id=vpn_type_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_vpn_type(obj=obj))

# TODO delete vpn type by id

if __name__ == "__main__":
    logging.info('Running...')
