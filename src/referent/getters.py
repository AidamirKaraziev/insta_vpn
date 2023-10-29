from typing import Optional
from referent.schemas import ReferentGet


def getting_referent(obj: ReferentGet) -> Optional[ReferentGet]:
    return ReferentGet(
        id=obj.id,
        telegram_id=obj.telegram_id,
        description=obj.description,
        referral_link=obj.referral_link,
        password=obj.password,
        sbp_number=obj.sbp_number
    )
