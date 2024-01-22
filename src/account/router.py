import logging

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import crud_account
from account.getters import getting_account
from account.schemas import AccountCreate, AccountUpdate
from core.raise_template import get_raise_new
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from auth.base_config import fastapi_users
from auth.models import User
from payment.crud import crud_payment
from payment.schemas import PaymentCreate
from config import THE_AMOUNT_OF_PAYMENT_FOR_A_REFERRAL, PAYMENT_TYPE_INCREASE
from referent.crud import crud_referent
from referent.schemas import ReferentNativeCreate

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
        user: User = Depends(current_active_superuser),
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
        user: User = Depends(current_active_superuser),
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
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_account.add_account(db=session, new_data=new_data)
    await get_raise_new(code)
    # создает payment на начисление реферальных рублей за привлечение клиента референту
    if new_data.referent_id is not None:
        payment_data = PaymentCreate(referent_id=new_data.referent_id,
                                     amount=THE_AMOUNT_OF_PAYMENT_FOR_A_REFERRAL,
                                     payment_type_id=PAYMENT_TYPE_INCREASE.id)
        payment, code, indexes = await crud_payment.create_payment(db=session, new_data=payment_data)
        await get_raise_new(code)
    referent_data = ReferentNativeCreate(telegram_id=obj.id)
    referent, code, indexes = await crud_referent.create_native_referent(db=session, new_data=referent_data)
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
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_account.update_account(db=session, update_data=update_data, id=account_id)
    await get_raise_new(code)
    return SingleEntityResponse(data=getting_account(obj=obj))


@router.get(
            path="/by-referent/{referent_id}",
            response_model=ListOfEntityResponse,
            name='get_accounts_by_referent_id',
            description='Вывод аккаунтов по referent_id'
            )
async def get_accounts_by_referent_id(
        referent_id: UUID4,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_account.get_accounts_by_referent_id(db=session, referent_id=referent_id)
    await get_raise_new(code)
    return ListOfEntityResponse(data=[getting_account(obj) for obj in objects])


if __name__ == "__main__":
    logging.info('Running...')
