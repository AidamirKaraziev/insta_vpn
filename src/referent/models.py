import uuid

from sqlalchemy import Column, String, MetaData, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from database import Base
from partner.models import Partner

metadata = MetaData()


class Referent(Base):
    __tablename__ = "referent"

    metadata = metadata
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger)

    description = Column(String)
    password = Column(String)
    balance = Column(Integer)
    partner_id = Column(Integer, ForeignKey(Partner.id, ondelete="SET NULL"))

    partner = relationship(Partner, backref="referents", lazy="joined")
