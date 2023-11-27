from typing import Optional
from pydantic import BaseModel, UUID4

from config import BASE_REFERENT_GIFT_DAYS, BASE_PARTNER
from partner.schemas import PartnerGet
from referent_type.schemas import ReferentTypeGet


# TODO add referent_type
class ReferentGet(BaseModel):
    id: UUID4
    telegram_id: Optional[int]

    gift_days: Optional[int]
    balance: Optional[int]
    partner: Optional[PartnerGet]
    referent_type: Optional[ReferentTypeGet]
    description: Optional[str]
    password: Optional[str]

    referral_link: Optional[str]


class ReferentCreate(BaseModel):
    telegram_id: int
    referent_type_id: Optional[int]

    gift_days: Optional[int] = BASE_REFERENT_GIFT_DAYS
    partner_id: Optional[int] = BASE_PARTNER

    description: Optional[str]
    password: Optional[str]


class ReferentUpdate(BaseModel):
    # partner_id: Optional[int]
    #
    gift_days: Optional[int]
    balance: Optional[int]

    # description: Optional[str]


class ReferentLink(BaseModel):
    referent_link: str


"""Мои размышления касательно двух типов рефералов"""
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
