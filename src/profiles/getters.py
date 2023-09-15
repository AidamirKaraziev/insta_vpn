from typing import Optional

from account.getters import getting_account
from profiles.schemas import ProfileGet
from server.getters import getting_server
from utils.time_stamp import to_timestamp


def getting_profile(obj: ProfileGet) -> Optional[ProfileGet]:
    # if obj.created_at is not None:
    #     obj.created_at = to_timestamp(obj.created_at)
    # if obj.date_end is not None:
    #     obj.date_end = to_timestamp(obj.date_end)
    date_end_str = obj.date_end.strftime('%Y-%m-%d %H:%M:%S')
    return ProfileGet(
        id=obj.id,
        account_id=obj.account_id,
        server_id=obj.server_id,
        key_id=obj.key_id,
        name=obj.name,
        port=obj.port,
        method=obj.method,
        access_url=obj.access_url,
        used_bytes=obj.used_bytes,
        data_limit=obj.data_limit,
        date_end=date_end_str,
        is_active=obj.is_active
    )
