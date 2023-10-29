from datetime import datetime

from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Boolean, MetaData, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
from referent.models import Referent

metadata = MetaData()


class Account(Base):
    __tablename__ = "account"

    metadata = metadata
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    name = Column(String)
    number = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    trial_is_active = Column(Boolean, default=True)
    referent_id = Column(UUID(as_uuid=True), ForeignKey(Referent.id, ondelete="SET NULL"))
    can_pay_out = Column(Boolean, default=True)

    referent = relationship(Referent, backref="accounts", lazy="joined")
