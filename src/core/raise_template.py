from core.exception import InaccessibleEntity, UnfoundEntity, UnprocessableEntity


async def get_raise(num: int, message: str):
    # Недоступный объект
    if num == 403:
        raise InaccessibleEntity(
            message=message,
            num=num,
            description=message,
            path="$.body"
        )
    # невозможно найти
    if num == 404:
        raise UnfoundEntity(
                message=message,
                num=num,
                description=message,
                path="$.body"
            )
    # эта операция не доступна для запрашиваемого
    if num == 422:
        raise UnprocessableEntity(
            message=message,
            num=num,
            description=message,
            path="$.body"
        )

    else:
        raise UnfoundEntity(
            message=f"АЙДАМИР ВНЕСИ RAISE {message, num}",
            num=999,
            description=f"АЙДАМИР ВНЕСИ RAISE {message, num}",
            path="$.body"
            )
