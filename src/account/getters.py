from typing import Optional
from account.schemas import AccountGet


def getting_account(obj: AccountGet) -> Optional[AccountGet]:
    return AccountGet(
        id=obj.id,
        name=obj.name,
        number=obj.number,
        created_at=obj.created_at,
    )
