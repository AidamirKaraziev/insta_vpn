from pydantic import BaseModel, Field
from profiles.schemas import ProfileGet
from tariff.schemas import TariffGet


class PaymentGet(BaseModel):
    id: int
    profile_id: ProfileGet
    tariff_id: TariffGet
    created_at: int


class PaymentCreate(BaseModel):
    profile_id: int
    tariff_id: int


class PaymentUpdate(BaseModel):
    pass
