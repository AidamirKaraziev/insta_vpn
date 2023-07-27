from typing import Optional
from ip_address.schemas import IpAddressGet


def getting_ip_address(obj: IpAddressGet) -> Optional[IpAddressGet]:
    return IpAddressGet(
        id=obj.id,
        name=obj.name,
        is_active=obj.is_active,
    )
