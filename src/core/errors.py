from traceback import extract_tb, format_list

from fastapi.exceptions import RequestValidationError
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.exception import EntityError, ListOfEntityError
from core.response import Error, SingleEntityResponse

# from exceptions import EntityError, ListOfEntityError

from main import app

# добавил я сам, возможно надо убрать!!!!!!
# from .core.celery_app import celery_app
# from config import settings


class SchemasError(BaseModel):
    num: int
    message: str


default_error_description = {
    400: 'Невалидные данные',
    401: 'Войдите в приложение ещё раз',
    403: 'Войдите в приложение ещё раз',
    404: 'Не найдено',
    422: 'Некоректные данные',
    500: 'Внутреняя ошибка сервера'
}


# @app.exception_handler(StarletteHTTPException)
# async def custom_http_exception_handler(request, exc: StarletteHTTPException):
#
#     if exc.status_code in settings.ERROR_NOTIFIER_CODES:
#         error_desc = '\n'.join(format_list(extract_tb(exc.__traceback__)))
#         celery_app.send_task("app.worker.test_celery", args=["error"])
#         celery_app.send_task("app.worker.error_notify", args=[error_desc])
#     return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc: RequestValidationError):
    errors = []

    for er in exc.errors():
        errors.append(
            Error(
                message=er['msg'],
                path='.'.join(str(p) for p in er['loc']) if er['type'] != 'value_error.jsondecode' else 'body'
            )
        )

    return JSONResponse(
        status_code=400,
        content=(
            SingleEntityResponse(
                message="Validation Error",
                errors=errors,
                description=default_error_description.get(400, 'Невалидные данные')
            )
        ).dict(),
    )


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):

    errors = [
        Error(
            message=exc.detail,
            path=None if exc.status_code not in {401, 403} else "header"
        )
    ]

    return JSONResponse(
        status_code=exc.status_code,
        content=(
            SingleEntityResponse(
                message="Error",
                errors=errors,
                description=default_error_description.get(exc.status_code, 'Ошибка')
            )
        ).dict(),
    )


@app.exception_handler(EntityError)
def entity_error_handler(request: Request, exc: EntityError):

    return JSONResponse(
        status_code=exc.http_status,
        content=(
            SingleEntityResponse(
                message="Error",
                errors=[
                    Error(
                        code=exc.num,
                        message=exc.message
                    )
                ],
                description=exc.message
            )
        ).dict(),
    )


@app.exception_handler(ListOfEntityError)
def entity_error_handler(request: Request, exc: ListOfEntityError):

    return JSONResponse(
        status_code=exc.http_status,
        content=(
            SingleEntityResponse(
                message="Error",
                errors=[
                    Error(
                        code=exc_item.num,
                        message=exc_item.message,
                        path=exc_item.path
                    )
                    for exc_item in exc.errors
                ],
                description=exc.description
            )
        ).dict(),
    )



