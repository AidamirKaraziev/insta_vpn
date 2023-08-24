from typing import Optional

from account.getters import getting_account
from outline.outline.outline_vpn.outline_vpn import OutlineKey
from profiles.schemas import ProfileGet
from test_outline.schemas import OutlineGet
from utils.time_stamp import to_timestamp


def getting_outline(obj: OutlineKey) -> Optional[OutlineGet]:
    return OutlineGet(
        key_id=obj.key_id,
        name=obj.name,
        port=obj.port,
        method=obj.method,
        access_url=obj.access_url,
        used_bytes=obj.used_bytes,
        data_limit=obj.data_limit
    )
