from typing import Optional

from partner.schemas import PartnerGet


def getting_partner(obj: PartnerGet) -> Optional[PartnerGet]:
    return PartnerGet(
        id=obj.id,
        name=obj.name,
    )
