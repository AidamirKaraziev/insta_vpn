from typing import Optional
from server.schemas import ServerGet


def getting_server(obj: ServerGet) -> Optional[ServerGet]:
    return ServerGet(
        id=obj.id,
        vpn_type_id=obj.vpn_type_id,
        name=obj.name,
        port=obj.port,
        address=obj.address,

        api_url=obj.api_url,
        cert_sha256=obj.cert_sha256,
        marzban_login=obj.marzban_login,
        marzban_pass=obj.marzban_pass,

        max_client=obj.max_client,
        fact_client=obj.fact_client,
        is_active=obj.is_active,
    )
