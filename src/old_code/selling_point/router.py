import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from old_code.auth.base_config import fastapi_users
from old_code.auth.models import User
from core.response import SingleEntityResponse, ListOfEntityResponse
from database import get_async_session
from old_code.selling_point.crud import crud_selling_point
from old_code.selling_point.getters import getting_selling_point
from old_code.selling_point.schemas import SellingPointCreate, SellingPointUpdate

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
current_active_user = fastapi_users.current_user(active=True)
current_active_client = fastapi_users.current_user(active=True, superuser=False)
BASE_PATH = "./static/"
PATH_MODEL = "selling_point"


router = APIRouter(
    prefix="/selling_point",
    tags=["SellingPoint"]
)


@router.get(
    path='/all',
    response_model=ListOfEntityResponse,
    name='get_selling_points',
    description='Получение списка точек сбыта'
)
async def get_selling_points(
        request: Request,
        limit: int = 100,
        skip: int = 0,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    selling_points, code, indexes = await crud_selling_point.get_all_selling_points(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_selling_point(obj, request) for obj in selling_points])


@router.get(
    path="/{selling_point_id}",
    response_model=SingleEntityResponse,
    name='get_selling_point_by_id',
    description='Вывод точки сбыта по идентификатору'
)
async def get_selling_point_by_id(
        request: Request,
        selling_point_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    selling_point, code, indexes = await crud_selling_point.get_selling_point_by_id(db=session,
                                                                                    selling_point_id=selling_point_id)
    if code != 0:
        raise HTTPException(status_code=404, detail=code)
    return SingleEntityResponse(data=getting_selling_point(obj=selling_point, request=request))


@router.post(
    path="/",
    response_model=SingleEntityResponse,
    name='create_selling_point',
    description='Добавление точки сбыта'
)
async def create_selling_point(
        request: Request,
        new_data: SellingPointCreate,
        user: User = Depends(current_active_client),
        session: AsyncSession = Depends(get_async_session),
):
    if user.is_superuser is True:
        raise HTTPException(status_code=409, detail="Контрольные точки создают клиенты!")
    new_data.client_id = user.id
    selling_point, code, indexes = await crud_selling_point.create_selling_point(db=session, new_data=new_data)
    if code != 0:
        raise HTTPException(status_code=409, detail=code)
    return SingleEntityResponse(data=getting_selling_point(obj=selling_point, request=request))


@router.put(
    path="/{selling_point_id}",
    response_model=SingleEntityResponse,
    name='update_selling_point',
    description='Изменить точку сбыта'
)
async def update_selling_point(
        request: Request,
        update_data: SellingPointUpdate,
        selling_point_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    # check id user
    ob, code, indexes = await crud_selling_point.get_selling_point_by_id(db=session, selling_point_id=selling_point_id)
    if user.is_superuser is False:
        if ob.client_id != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
    selling_point, code, indexes = await crud_selling_point.update_selling_point(db=session,
                                                                                 update_data=update_data,
                                                                                 selling_point_id=selling_point_id)
    if code != 0:
        raise HTTPException(status_code=404, detail="Resource with this ID does not exist")
    return SingleEntityResponse(data=getting_selling_point(obj=selling_point, request=request))


@router.put("/add-file/",
            response_model=SingleEntityResponse,
            name='add_file',
            description='Добавить фото'
            )
async def add_file(
        request: Request,
        which_photo_name: str,
        selling_point_id: int,
        file: Optional[UploadFile] = File(None),
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
        ):
    bad_witch_photo_name = await crud_selling_point.check_name(witch_name=which_photo_name)
    if bad_witch_photo_name is not None:
        raise HTTPException(status_code=400, detail=bad_witch_photo_name)

    selling_point, code, indexes = await crud_selling_point.get_selling_point_by_id(
        db=session, selling_point_id=selling_point_id)
    if code != 0:
        raise HTTPException(status_code=404, detail=code)

    save_path = await crud_selling_point.adding_file(
        db=session, file=file, path_model=PATH_MODEL,
        path_type=which_photo_name, db_obj=selling_point, base_path=BASE_PATH)
    if not save_path:
        return HTTPException(status_code=400, detail=f"Not have save photo")
    return SingleEntityResponse(data=getting_selling_point(selling_point, request=request))


if __name__ == "__main__":
    logging.info('Running...')
