from core.exception import InaccessibleEntity


async def getting_raise(code: str):
    raise InaccessibleEntity(
        message=code,
        num=400,
        description=code,
        path="$.body"
    )
