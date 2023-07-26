import logging
import shutil
import time
import os
from typing import Optional, Type

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status,  UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi_users import exceptions, models
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.router.common import ErrorCode, ErrorModel

from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import fastapi_users
from auth.manager import get_user_manager
from auth.models import User
from auth.schemas import UserCreate, UserRead, UserUpdate
from core.response import ListOfEntityResponse, SingleEntityResponse
from database import get_async_session

from user.crud import crud_user
from user.getters import getting_user


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "upload")

timestr = time.strftime("%Y%m%d-%H%M%S")
BASE_PATH = "./static/"
PATH_MODEL = "user"
PATH_PHOTO = "photo"

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
current_active_user = fastapi_users.current_user(active=True)


router = APIRouter(
    prefix="/users",
    tags=["users"]
)
router.mount("/static", StaticFiles(directory="static"), name="static")


@router.get(
            path='/all/',
            response_model=ListOfEntityResponse,
            name='get_users',
            description='Получение списка всех рекламируемых групп'
            )
async def get_users(
        request: Request,
        skip: int = 0,
        limit: int = 100,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    objects, code, indexes = await crud_user.get_all_users(db=session, skip=skip, limit=limit)
    return ListOfEntityResponse(data=[getting_user(obj, request=request) for obj in objects])


@router.post(
    path="/create-admin/",
    response_model=SingleEntityResponse,
    status_code=status.HTTP_201_CREATED,
    name="create_admin",
    description="Создание админа",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.REGISTER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def create_admin(
    request: Request,
    user_create: UserCreate,  # type: ignore
    user: User = Depends(current_active_superuser),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    try:
        created_user = await user_manager.create_admin(
            user_create, safe=True, request=request
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    return SingleEntityResponse(data=getting_user(obj=user, request=request))


@router.post('file/upload/')
async def upload_file(file: UploadFile):
    if file.content_type != "image/png" and "image/jpeg":
        return HTTPException(status_code=400, detail=f"invalid content type {file.content_type}")
    return {"content": file.file, "filename": file.filename, "size": file.size, "content_type": file.content_type}


@router.post("/file/upload-download/")
async def upload_n_download(file: UploadFile):
    if file.content_type != "image/png" and "image/jpeg":
        return HTTPException(status_code=400, detail=f"invalid content type {file.content_type}")
    new_filename = file.filename
    # new_filename = "{}_{}".format(os.path.splitext(file.filename)[0], timestr)
    SAVE_FILE_PATH = os.path.join(UPLOAD_DIR, new_filename)
    with open(SAVE_FILE_PATH, "wb") as wf:
        shutil.copyfileobj(file.file, wf)
        file.file.close()

    return FileResponse(path=SAVE_FILE_PATH, media_type="application/octet-stream", filename=new_filename)


@router.put("/me/add-photo/",
            response_model=SingleEntityResponse,
            name='add_photo',
            description='Добавить фото'
            )
async def add_photo(
        request: Request,
        file: Optional[UploadFile] = File(None),
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
        ):
    save_path = await crud_user.adding_file(
        db=session, file=file, path_model=PATH_MODEL,
        path_type=PATH_PHOTO, db_obj=user, base_path=BASE_PATH)
    if not save_path:
        return HTTPException(status_code=400, detail=f"Not have save photo")
    return SingleEntityResponse(data=getting_user(user, request=request))


def get_users_router(
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    user_schema: Type[UserRead],
    user_update_schema: Type[UserUpdate],
    # authenticator: Authenticator,
    requires_verification: bool = False,
) -> APIRouter:
    router = APIRouter()

    get_current_active_user = fastapi_users.current_user(
        active=True, verified=requires_verification
    )
    get_current_superuser = fastapi_users.current_user(
        active=True, verified=requires_verification, superuser=True
    )

    async def get_user_or_404(
        id: str,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ) -> models.UP:
        try:
            parsed_id = user_manager.parse_id(id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID) as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    @router.get(
        "/me",
        response_model=SingleEntityResponse,
        name="users:current_user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user.",
            },
        },
    )
    async def me(
        request: Request,
        user: models.UP = Depends(get_current_active_user),
    ):
        return SingleEntityResponse(data=getting_user(obj=user, request=request))

    @router.patch(
        "/me",
        response_model=SingleEntityResponse,
        dependencies=[Depends(get_current_active_user)],
        name="users:patch_current_user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user.",
            },
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                        "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
    )
    async def update_me(
        request: Request,
        user_update: user_update_schema,
        user: models.UP = Depends(get_current_active_user),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.update(
                user_update, user, safe=True, request=request)

            return SingleEntityResponse(data=getting_user(obj=user, request=request))
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
            )

    @router.get(
        "/{id}",
        response_model=SingleEntityResponse,
        dependencies=[Depends(get_current_superuser)],
        name="users:user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user.",
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Not a superuser.",
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "The user does not exist.",
            },
        },
    )
    async def get_user(request: Request, user=Depends(get_user_or_404)):
        return SingleEntityResponse(data=getting_user(obj=user, request=request))

    @router.patch(
        "/{id}",
        response_model=SingleEntityResponse,
        dependencies=[Depends(get_current_superuser)],
        name="users:patch_user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user.",
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Not a superuser.",
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "The user does not exist.",
            },
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                        "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
    )
    async def update_user(
        user_update: user_update_schema,
        request: Request,
        user=Depends(get_user_or_404),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.update(
                user_update, user, safe=False, request=request)

            return SingleEntityResponse(data=getting_user(obj=user, request=request))
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
            )

    return router


if __name__ == "__main__":
    logging.info('Running...')
