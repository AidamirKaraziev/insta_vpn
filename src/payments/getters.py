from typing import Optional
from payments.schemas import PaymentGet
from profiles.getters import getting_profile
from tariff.getters import getting_tariff
from utils.time_stamp import to_timestamp


def getting_payment(obj: PaymentGet) -> Optional[PaymentGet]:
    # if obj.created_at is not None:
    #     obj.created_at = to_timestamp(obj.created_at)
    return PaymentGet(
        id=obj.id,
        profile_id=getting_profile(obj.profile) if obj.profile is not None else None,
        tariff_id=getting_tariff(obj.tariff) if obj.tariff is not None else None,
        created_at=obj.created_at
    )
