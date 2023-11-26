from typing import Optional
from pydantic import BaseModel, UUID4

from config import BASE_REFERENT_GIFT_DAYS, BASE_PARTNER


class ReferentGet(BaseModel):
    id: UUID4
    telegram_id: Optional[int]

    gift_days: Optional[int]
    balance: Optional[int]
    partner_id: Optional[int]

    description: Optional[str]
    password: Optional[str]

    referral_link: Optional[str]


class ReferentCreate(BaseModel):
    telegram_id: Optional[int]

    gift_days: Optional[int] = BASE_REFERENT_GIFT_DAYS
    partner_id: Optional[int] = BASE_PARTNER

    description: Optional[str]
    password: Optional[str]


class ReferentUpdate(BaseModel):
    partner_id: Optional[int]

    gift_days: Optional[int]
    balance: Optional[int]

    description: Optional[str]


class ReferentLink(BaseModel):
    referent_link: str

#
# class ReferentCreateNative(BaseModel):
#     telegram_id: Optional[int]
#
#     gift_days: Optional[int] = BASE_REFERENT_GIFT_DAYS
#     partner_id: Optional[int] = BASE_PARTNER
#
#
# class ReferentCreateBlogger(BaseModel):
#     gift_days: Optional[int] = BASE_REFERENT_GIFT_DAYS
#     partner_id: Optional[int] = BASE_PARTNER
#
#     description: Optional[str]
#     password: Optional[str]
