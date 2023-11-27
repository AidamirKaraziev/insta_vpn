from typing import Optional

from vpn_type.schemas import VpnTypeGet


def getting_vpn_type(obj: VpnTypeGet) -> Optional[VpnTypeGet]:
    return VpnTypeGet(
        id=obj.id,
        name=obj.name,
    )
