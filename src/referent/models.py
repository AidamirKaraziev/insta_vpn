import uuid

from sqlalchemy import Column, String, MetaData, BigInteger
from database import Base
from sqlalchemy.dialects.postgresql import UUID


metadata = MetaData()


class Referent(Base):
    __tablename__ = "referent"

    metadata = metadata
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger)

    description = Column(String)
    referral_link = Column(String)
    password = Column(String)
    sbp_number = Column(String)
