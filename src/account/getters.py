from typing import Optional
from account.schemas import AccountGet


def getting_account(obj: AccountGet) -> Optional[AccountGet]:
    formatted_timestamp = obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    return AccountGet(
        id=obj.id,
        name=obj.name,
        number=obj.number,
        created_at=formatted_timestamp
    )
