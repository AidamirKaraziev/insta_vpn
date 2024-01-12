from typing import Optional

from pydantic import UUID4

from config import BASE_REFERRAL_LINK
from partner.getters import getting_partner
from referent.schemas import ReferentGet
from referent_type.getters import getting_referent_type


def gen_referral_link(referent_id: UUID4):
    return f"{BASE_REFERRAL_LINK}referral-{referent_id}"


def getting_referent(obj: ReferentGet) -> Optional[ReferentGet]:
    return ReferentGet(
        id=obj.id,
        telegram_id=obj.telegram_id,
        gift_days=obj.gift_days,
        balance=obj.balance,
        partner=getting_partner(obj.partner) if obj.partner is not None else None,
        referent_type=getting_referent_type(obj.referent_type) if obj.referent_type is not None else None,
        description=obj.description,
        budget_amount=obj.budget_amount,

        referral_link=gen_referral_link(referent_id=obj.id),
    )
