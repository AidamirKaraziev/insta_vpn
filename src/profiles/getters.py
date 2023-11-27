from typing import Optional

from pydantic import UUID4

from config import CONN_NAME, OUTLINE_USERS_GATEWAY

from profiles.schemas import ProfileGet


def gen_outline_dynamic_link(profile_id: UUID4):
    return f"{OUTLINE_USERS_GATEWAY}/outline/{profile_id}#{CONN_NAME}"


def getting_profile(obj: ProfileGet) -> Optional[ProfileGet]:
    if obj.date_end is not None:
        obj.date_end = obj.date_end.strftime('%Y-%m-%d %H:%M:%S')
    else:
        obj.date_end = None
    dynamic_key = gen_outline_dynamic_link(profile_id=obj.id)
    return ProfileGet(
        id=obj.id,
        name=obj.name,
        account_id=obj.account_id,

        dynamic_key=dynamic_key,
        outline_key_id=obj.outline_key_id,

        date_end=obj.date_end,
        used_bytes=obj.used_bytes,

        is_active=obj.is_active,
    )
