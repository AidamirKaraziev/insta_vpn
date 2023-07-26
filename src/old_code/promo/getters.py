from typing import Optional

from old_code.promo.schemas import PromoGet


def getting_promo(obj: PromoGet) -> Optional[PromoGet]:
    return PromoGet(
        id=obj.id,
        name=obj.name,
        is_active=obj.is_active,
    )
