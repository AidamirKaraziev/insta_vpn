from typing import Optional

from payment.schemas import PaymentGet
from payment_type.getters import getting_payment_type
from status.getters import getting_status


def getting_payment(obj: PaymentGet) -> Optional[PaymentGet]:
    return PaymentGet(
        id=obj.id,
        referent_id=obj.referent_id,
        amount=obj.amount,
        spb_number=obj.spb_number,
        card_number=obj.spb_number,
        created_at=obj.created_at,
        payment_type=getting_payment_type(obj.payment_type) if obj.payment_type is not None else None,
        status=getting_status(obj.status) if obj.status is not None else None,
    )
