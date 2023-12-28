from typing import Optional
from pydantic import BaseModel, UUID4

from config import BLOGGER_REFERENT_TYPE, BASE_REFERENT_GIFT_DAYS, GENERAL_PARTNER, NATIVE_REFERENT_TYPE
from partner.schemas import PartnerGet
from referent_type.schemas import ReferentTypeGet


class ReferentGet(BaseModel):
    id: UUID4
    telegram_id: Optional[int]

    gift_days: Optional[int]
    balance: Optional[int]
    partner: Optional[PartnerGet]
    referent_type: Optional[ReferentTypeGet]
    description: Optional[str]
    budget_amount: Optional[int]

    referral_link: Optional[str]


class ReferentCreate(BaseModel):
    referent_type_id: Optional[int]
    gift_days: Optional[int]
    partner_id: Optional[int]

    class Config:
        arbitrary_types_allowed = True


class ReferentNativeCreate(ReferentCreate):
    telegram_id: int
    referent_type_id: Optional[int] = NATIVE_REFERENT_TYPE.id
    gift_days: Optional[int] = BASE_REFERENT_GIFT_DAYS
    partner_id: Optional[int] = GENERAL_PARTNER.id


class ReferentCompanyCreate(ReferentCreate):
    referent_type_id: int = BLOGGER_REFERENT_TYPE.id
    gift_days: int = BASE_REFERENT_GIFT_DAYS
    partner_id: int = GENERAL_PARTNER.id
    description: Optional[str]
    budget_amount: Optional[int]


class ReferentUpdate(BaseModel):
    gift_days: Optional[int]
    balance: Optional[int]
