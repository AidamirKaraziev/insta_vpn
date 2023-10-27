from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
from referral.models import Referral

metadata = MetaData()


class Account(Base):
    __tablename__ = "account"

    metadata = metadata
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    name = Column(String)
    number = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    trial = Column(Boolean, default=False)
    referral_id = Column(UUID(as_uuid=True), ForeignKey(Referral.id, ondelete="SET NULL"))

    referral = relationship(Referral, backref="accounts", lazy="joined")
