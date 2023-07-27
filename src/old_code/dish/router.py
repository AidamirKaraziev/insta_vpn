import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from old_code.auth.base_config import fastapi_users
from old_code.auth.models import User
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from old_code.dish.crud import crud_dish
from old_code.dish.getters import getting_dish
from old_code.dish.schemas import DishCreate, DishUpdate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
current_active_user = fastapi_users.current_user(active=True)
BASE_PATH = "./static/"
PATH_MODEL = "dish"


router = APIRouter(
    prefix="/dish",
    tags=["Dish"]
)


@router.get(
    path='/all',
    response_model=ListOfEntityResponse,
    name='get_dishes',
    description='Получение списка всех блюд'
)
async def get_dishes(
        request: Request,
        limit: int = 100,
        skip: int = 0,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    dishes, code, indexes = await crud_dish.get_all_dishes(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_dish(dish, request=request) for dish in dishes])


@router.get(
    path="/{dish_id}",
    response_model=SingleEntityResponse,
    name='get_dish_by_id',
    description='Вывод блюда по идентификатору'
)
async def get_dish_by_id(
        request: Request,
        dish_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    dish, code, indexes = await crud_dish.get_dish_by_id(db=session, dish_id=dish_id)
    # ошибки обработать
    if code != 0:
        raise HTTPException(status_code=404, detail=code)
    return SingleEntityResponse(data=getting_dish(obj=dish, request=request))



@router.post(
    path="/",
    response_model=SingleEntityResponse,
    name='create_dish',
    description='Добавление блюда'
)
async def create_dish(
        request: Request,
        new_data: DishCreate,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    obj, code, indexes = await crud_dish.create_dish(db=session, new_data=new_data)
    if code != 0:
        raise HTTPException(status_code=409, detail=code)
    return SingleEntityResponse(data=getting_dish(obj=obj, request=request))
    

@router.put(
    path="/{dish_id}",
    response_model=SingleEntityResponse,
    name='update_dish',
    description='Изменение блюда'
)
async def update_dish(
        request: Request,
        update_data: DishUpdate,
        dish_id: int,
        user: User = Depends(current_active_superuser),
        session: AsyncSession = Depends(get_async_session),
):
    dish, code, indexes = await crud_dish.update_dish(db=session,
                                                      update_data=update_data,
                                                      dish_id=dish_id)
    if code != 0:
        raise HTTPException(status_code=404, detail=code)
    return SingleEntityResponse(data=getting_dish(obj=dish, request=request))


@router.put("/add-file/",
            response_model=SingleEntityResponse,
            name='add_file',
            description='Добавить фото'
            )
async def add_file(
        request: Request,
        which_photo_name: str,
        dish_id: int,
        file: Optional[UploadFile] = File(None),
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
        ):
    bad_witch_photo_name = await crud_dish.check_name(witch_name=which_photo_name)
    if bad_witch_photo_name is not None:
        raise HTTPException(status_code=400, detail=bad_witch_photo_name)

    dish, code, indexes = await crud_dish.get_dish_by_id(
        db=session, dish_id=dish_id)
    if code != 0:
        raise HTTPException(status_code=404, detail=code)

    save_path = await crud_dish.adding_file(
        db=session, file=file, path_model=PATH_MODEL,
        path_type=which_photo_name, db_obj=dish, base_path=BASE_PATH)
    if not save_path:
        return HTTPException(status_code=400, detail=f"Not have save photo")
    return SingleEntityResponse(data=getting_dish(dish, request=request))


if __name__ == "__main__":
    logging.info('Running...')
