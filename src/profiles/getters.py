from typing import Optional

from profiles.schemas import ProfileGet


def getting_profile(obj: ProfileGet) -> Optional[ProfileGet]:
    if obj.date_end is not None:
        obj.date_end = obj.date_end.strftime('%Y-%m-%d %H:%M:%S')
    else:
        obj.date_end = None
    return ProfileGet(
        id=obj.id,
        name=obj.name,
        account_id=obj.account_id,
        dynamic_key=obj.dynamic_key,
        static_key_id=obj.static_key_id,
        date_end=obj.date_end,
        used_bytes=obj.used_bytes,
        is_active=obj.is_active
    )
