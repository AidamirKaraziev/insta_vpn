from typing import Optional

from account.schemas import AccountGet
from utils.time_stamp import to_timestamp


def getting_account(obj: AccountGet) -> Optional[AccountGet]:
    if obj.created_at is not None:
        obj.created_at = to_timestamp(obj.created_at)
    return AccountGet(
        id=obj.id,
        name=obj.name,
        number=obj.number,
        telegram_id=obj.telegram_id,
        created_at=obj.created_at,
        time_zone=obj.time_zone
    )
