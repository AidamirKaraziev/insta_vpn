import uuid

from sqlalchemy import Column, String, MetaData, BigInteger, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from database import Base
from partner.models import Partner
from referent_type.models import ReferentType

metadata = MetaData()


class Referent(Base):
    __tablename__ = "referent"

    metadata = metadata
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger)
    partner_id = Column(Integer, ForeignKey(Partner.id, ondelete="SET NULL"))
    referent_type_id = Column(Integer, ForeignKey(ReferentType.id, ondelete="SET NULL"))

    gift_days = Column(Integer)
    balance = Column(Integer, default=0)

    description = Column(String)
    password = Column(String)

    partner = relationship(Partner, backref="referents", lazy="joined")
    referent_type = relationship(ReferentType, backref="referents", lazy="joined")
    __table_args__ = (
            UniqueConstraint("telegram_id", "referent_type_id", name='_telegram_referent_type_uc'),
                          )

