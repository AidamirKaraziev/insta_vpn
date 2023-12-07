from typing import Optional

from payment.schemas import PaymentGet
from status.getters import getting_status


def getting_payment(obj: PaymentGet) -> Optional[PaymentGet]:
    return PaymentGet(
        id=obj.id,
        referent_id=obj.referent_id,
        amount=obj.amount,
        spb_number=obj.spb_number,
        card_number=obj.spb_number,
        created_at=obj.created_at,
        status=getting_status(obj.status) if obj.status is not None else None,
    )
