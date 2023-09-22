import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import crud_account
from config import FREE_TRAFFIC
from core.raise_template import get_raise
from core.response import SingleEntityResponse, ListOfEntityResponse, OkResponse
from database import get_async_session

from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from profiles.crud import crud_profile
from profiles.getters import getting_profile
from profiles.schemas import ProfileCreate
from server.crud import crud_server
from tariff.crud import crud_tariff
from outline_apis.getters import getting_outline
from outline_apis.schemas import OutlineCreate, OutlineUpdate

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
            path="/create/{account_id}/{tariff_id}/",
            response_model=SingleEntityResponse,
            name='create_new_key',
            description='создание'
            )
async def create_new_key(
        account_id: int,
        tariff_id: int,
        new_data: OutlineCreate,

        # user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    account, code, indexes = await crud_account.get_account_by_id(db=session, id=account_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    tariff, code, indexes = await crud_tariff.get_tariff_by_id(db=session, id=tariff_id)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    # get_good_server
    server, code, indexes = await crud_server.get_good_server(db=session)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
    new_key = client.create_key(key_name=new_data.name)
    profile = ProfileCreate(account_id=account_id, server_id=server.id, key_id=new_key.key_id, name=new_key.name,
                            port=new_key.port, method=new_key.method, access_url=new_key.access_url,
                            used_bytes=new_key.used_bytes, data_limit=new_key.data_limit)
    profile, code, indexes = await crud_profile.add_profile(db=session, new_data=profile)
    if code != 0:
        await get_raise(num=code["num"], message=code["message"])
    return SingleEntityResponse(data=getting_profile(obj=profile))


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


@router.delete(path="/{key_id}",
               response_model=SingleEntityResponse,
               name='delete_key',
               description='Удалить ключ'
               )
async def delete_key(
        key_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj = client.delete_key(key_id)
    return SingleEntityResponse(data=obj)


@router.get(path="/test/{key_id}",
            response_model=SingleEntityResponse,
            name='test_api',
            description='Тестирование АПИ'
            )
async def test_api(
        key_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    status = client.add_data_limit(key_id=key_id, limit_bytes=FREE_TRAFFIC)
    # status = client.delete_data_limit(key_id=key_id)
    return SingleEntityResponse(data=status)

if __name__ == "__main__":
    logging.info('Running...')
