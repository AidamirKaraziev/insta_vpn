from typing import Optional

from pydantic import UUID4

from config import BASE_REGISTER_REFERENT_LINK, BASE_REFERRAL_LINK
from referent.schemas import ReferentGet, ReferentLink


def gen_referral_link(referent_id: UUID4):
    return f"{BASE_REFERRAL_LINK}/referral/{referent_id}"


def gen_referent_link(referent_id: UUID4):
    return f"{BASE_REGISTER_REFERENT_LINK}/referent/{referent_id}"


def getting_referent(obj: ReferentGet) -> Optional[ReferentGet]:
    return ReferentGet(
        id=obj.id,
        telegram_id=obj.telegram_id,
        gift_days=obj.gift_days,
        balance=obj.balance,
        partner_id=obj.partner_id,

        description=obj.description,
        password=obj.password,

        referral_link=gen_referral_link(referent_id=obj.id),
    )


# def getting_referent_link(obj: ReferentLink) -> Optional[ReferentLink]:
#     return ReferentLink(
#         referent_link=obj.referent_link
#     )
