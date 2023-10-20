from typing import List


class EntityError(ValueError):

    http_status = 400

    def __init__(self, message=None, description=None, num=0, path=None):
        self.message = message
        self.num = num
        self.description = description
        self.path = path


# невозможно найти
class UnfoundEntity(EntityError):
    http_status = 404


# Недоступный объект
class InaccessibleEntity(EntityError):
    http_status = 403


# эта операция не доступна для запрашиваемого
class UnprocessableEntity(EntityError):
    http_status = 422


class ListOfEntityError(ValueError):
    def __init__(self, errors: List[EntityError], description: str, http_status: int):
        self.errors = errors
        self.description = description
        self.http_status = http_status


async def exception_schemas(ex: Exception):
    return {"num": 403, "message": f"{ex}"}