import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import crud_account
from account.getters import getting_account
from account.schemas import AccountCreate, AccountUpdate
from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from auth.base_config import fastapi_users
from auth.models import User

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


router = APIRouter(
    prefix="/account",
    tags=["Account"]
)


@router.get(
            path='/all',
            response_model=ListOfEntityResponse,
            name='get_accounts',
            description='Получение списка всех аккаунтов'
            )
async def get_accounts(
        skip: int = 0,
        limit: int = 1000,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_account.get_all_accounts(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_account(obj) for obj in objects])


@router.get(
            path="/{account_id}",
            response_model=SingleEntityResponse,
            name='get_account',
            description='Вывод аккаунта по идентификатору'
            )
async def get_account(
        account_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_account.get_account_by_id(db=session, id=account_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_account(obj=obj))


@router.post(path="/",
             response_model=SingleEntityResponse,
             name='add_account',
             description='Добавить аккаунт'
             )
async def add_account(
        new_data: AccountCreate,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_account.add_account(db=session, new_data=new_data)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_account(obj=obj))


@router.put(path="/{account_id}",
            response_model=SingleEntityResponse,
            name='update_account',
            description='Изменить аккаунт'
            )
async def update_account(
        update_data: AccountUpdate,
        account_id: int,
        # user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_account.update_account(db=session, update_data=update_data, id=account_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_account(obj=obj))

# TODO get_accounts_by_referent_id


if __name__ == "__main__":
    logging.info('Running...')
