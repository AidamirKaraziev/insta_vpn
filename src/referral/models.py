import uuid

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData, BigInteger
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.dialects.postgresql import UUID
from partner.models import Partner


metadata = MetaData()


class Referral(Base):
    __tablename__ = "referral"

    metadata = metadata
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id = Column(Integer, ForeignKey(Partner.id, ondelete="SET NULL"))

    description = Column(String)
    referral_link = Column(String)
    password = Column(String)

    partner = relationship(Partner, backref="referrals", lazy="joined")
