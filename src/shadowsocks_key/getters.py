from typing import Optional
from shadowsocks_key.schemas import ShadowsocksKeyGet


def getting_shadowsocks_key(obj: ShadowsocksKeyGet) -> Optional[ShadowsocksKeyGet]:
    return ShadowsocksKeyGet(
        id=obj.id,
        server_id=obj.server_id,

        key_id=obj.key_id,
        name=obj.name,
        port=obj.port,
        method=obj.method,
        access_url=obj.access_url,
        used_bytes=obj.used_bytes,
        data_limit=obj.data_limit,
        password=obj.password,

        is_active=obj.is_active
    )
