from typing import Optional
from tariff.schemas import TariffGet


def getting_tariff(obj: TariffGet) -> Optional[TariffGet]:
    return TariffGet(
        id=obj.id,
        name=obj.name,
        price=obj.price,
        period_unix=obj.period_unix,
        is_active=obj.is_active,
    )
