import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session

from outline.outline.outline_vpn.outline_vpn import OutlineVPN

# from old_code.auth.base_config import fastapi_users
# from old_code.auth.models import User
# current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
# current_active_user = fastapi_users.current_user(active=True)
from test_outline.getters import getting_outline
from test_outline.schemas import OutlineCreate, OutlineUpdate

router = APIRouter(
    prefix="/outline",
    tags=["Outline"]
)
client = OutlineVPN(api_url="https://2.59.183.37:38411/bVPmyljNmp4S0sDJItaBXA",
                    cert_sha256="C3460EBF84BD01A6030F31EB46B06EE6E1690781204E95D88CE9CB0731DE8098")


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_outline_keys',
            description='Получение списка всех ключей'
            )
async def get_outline_keys(
        skip: int = 0,
        limit: int = 100,
):
    return ListOfEntityResponse(data=[getting_outline(obj) for obj in client.get_keys()])


@router.post(
            path="/create/",
            response_model=SingleEntityResponse,
            name='create_new_key',
            description='создание'
            )
async def create_new_key(
        new_data: OutlineCreate,
        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):

    new_key = client.create_key(key_name=new_data.name)

    return SingleEntityResponse(data=getting_outline(obj=new_key))


# @router.post(path="/",
#              response_model=SingleEntityResponse,
#              name='add_ip_address',
#              description='Добавить ip адрес'
#              )
# async def add_ip_address(
#         new_data: IpAddressCreate,
#         # user: User = Depends(current_active_superuser),
#         session: AsyncSession = Depends(get_async_session),
# ):
#     obj, code, indexes = await crud_ip_address.add_ip_address(db=session, new_data=new_data)
#     if code != 0:
#         await get_raise(num=code["num"], message=code["message"])
#     return SingleEntityResponse(data=getting_ip_address(obj=obj))


@router.put(path="/{key_id}",
            response_model=SingleEntityResponse,
            name='rename_key',
            description='переименовать ключ'
            )
async def rename_key(
        key_id: int,
        update_data: OutlineUpdate,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj = client.rename_key(key_id, update_data.name)
    return SingleEntityResponse(data=obj)


if __name__ == "__main__":
    logging.info('Running...')
