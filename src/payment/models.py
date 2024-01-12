import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, MetaData, ForeignKey, TIMESTAMP
from database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from payment_type.models import PaymentType
from referent.models import Referent
from status.models import Status

metadata = MetaData()


class Payment(Base):
    __tablename__ = "payment"

    metadata = metadata
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referent_id = Column(UUID(as_uuid=True), ForeignKey(Referent.id, ondelete="SET NULL"))
    amount = Column(Integer)
    spb_number = Column(String)
    card_number = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    status_id = Column(Integer, ForeignKey(Status.id, ondelete="SET NULL", onupdate="CASCADE"))
    payment_type_id = Column(Integer, ForeignKey(PaymentType.id, ondelete="SET NULL", onupdate="CASCADE"))

    referent = relationship(Referent, backref="payments", lazy="joined")
    status = relationship(Status, backref="payments", lazy="joined")
    payment_type = relationship(PaymentType, backref="payments", lazy="joined")
