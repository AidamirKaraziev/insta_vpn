from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData
from sqlalchemy.orm import relationship

from database import Base
from profiles.models import Profile
from tariff.models import Tariff

metadata = MetaData()


class Payment(Base):
    __tablename__ = "payment"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey(Profile.id, ondelete="SET NULL"), nullable=False)
    tariff_id = Column(Integer, ForeignKey(Tariff.id, ondelete="SET NULL"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    profile = relationship(Profile, backref="payments", lazy="joined")
    tariff = relationship(Tariff, backref="payments", lazy="joined")
