import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise
from ip_address.crud import crud_ip_address
from ip_address.getters import getting_ip_address
from ip_address.shcemas import IpAddressCreate, IpAddressUpdate
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session


# from old_code.auth.base_config import fastapi_users
# from old_code.auth.models import User
# current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
# current_active_user = fastapi_users.current_user(active=True)

router = APIRouter(
    prefix="/ip_address",
    tags=["Ip Address"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_ip_addresses',
            description='Получение списка всех ip адресов'
            )
async def get_ip_addresses(
        skip: int = 0,
        limit: int = 100,
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_ip_address.get_all_ips_addresses(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_ip_address(obj) for obj in objects])


@router.get(
            path="/{ip_address_id}",
            response_model=SingleEntityResponse,
            name='get_ip_address',
            description='Вывод ip адреса по идентификатору'
            )
async def get_ip_address(
        ip_address_id: int,
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_ip_address.get_ip_address_by_id(db=session, ip_address_id=ip_address_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_ip_address(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_ip_address',
             description='Добавить ip адрес'
             )
async def add_ip_address(
        new_data: IpAddressCreate,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_ip_address.add_ip_address(db=session, new_data=new_data)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_ip_address(obj=obj))


@router.put(path="/{ip_address_id}",
            response_model=SingleEntityResponse,
            name='update_ip_address',
            description='Изменить ip адрес'
            )
async def update_ip_address(
        update_data: IpAddressUpdate,
        ip_address_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_ip_address.update_ip_address(db=session, update_data=update_data,
                                                                 ip_address_id=ip_address_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_ip_address(obj=obj))


if __name__ == "__main__":
    logging.info('Running...')
