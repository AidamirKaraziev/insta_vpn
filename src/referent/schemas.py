from typing import Optional
from pydantic import BaseModel, UUID4


class ReferentGet(BaseModel):
    id: UUID4
    telegram_id: Optional[int]

    description: Optional[str]
    referral_link: Optional[str]
    password: Optional[str]


class ReferentCreate(BaseModel):
    id: UUID4
    telegram_id: Optional[int]

    description: Optional[str]
    referral_link: Optional[str]
    password: Optional[str]


class ReferentUpdate(BaseModel):
    telegram_id: Optional[int]

    description: Optional[str]
    referral_link: Optional[str]
    password: Optional[str]
