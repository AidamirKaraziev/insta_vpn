from typing import Optional

from payment_type.schemas import PaymentTypeGet


def getting_payment_type(obj: PaymentTypeGet) -> Optional[PaymentTypeGet]:
    return PaymentTypeGet(
        id=obj.id,
        name=obj.name,
    )
