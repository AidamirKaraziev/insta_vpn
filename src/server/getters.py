from typing import Optional
from server.schemas import ServerGet


def getting_server(obj: ServerGet) -> Optional[ServerGet]:
    return ServerGet(
        id=obj.id,
        name=obj.name,
        api_url=obj.api_url,
        cert_sha256=obj.cert_sha256,
        max_client=obj.max_client,
        fact_client=obj.fact_client,
        is_active=obj.is_active,
    )
