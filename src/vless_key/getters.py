from typing import Optional

from vless_key.shcemas import VlessKeyGet


def getting_vless_key(obj: VlessKeyGet) -> Optional[VlessKeyGet]:
    return VlessKeyGet(
        id=obj.id,
        link=obj.link,
        server_ip=obj.server_ip,
        is_active=obj.is_active
    )
