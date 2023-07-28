from typing import Optional

from account.getters import getting_account
from ip_address.getters import getting_ip_address
from profiles.schemas import ProfileGet
from utils.time_stamp import to_timestamp


def getting_profile(obj: ProfileGet) -> Optional[ProfileGet]:
    if obj.created_at is not None:
        obj.created_at = to_timestamp(obj.created_at)
    if obj.date_end is not None:
        obj.date_end = to_timestamp(obj.date_end)
    return ProfileGet(
        id=obj.id,
        account_id=getting_account(obj.account) if obj.account is not None else None,
        ip_address_id=getting_ip_address(obj.ip_address) if obj.ip_address is not None else None,
        peer_name=obj.peer_name,
        date_end=obj.date_end,
        created_at=obj.created_at,
        is_active=obj.is_active
    )
