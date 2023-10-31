from typing import Optional
from account.schemas import AccountGet


def getting_account(obj: AccountGet) -> Optional[AccountGet]:
    if obj.created_at is not None:
        obj.created_at = obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    return AccountGet(
        id=obj.id,
        name=obj.name,
        number=obj.number,
        created_at=obj.created_at,
        can_pay_out=obj.can_pay_out
    )
