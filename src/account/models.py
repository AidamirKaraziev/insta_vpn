from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData
from database import Base


metadata = MetaData()


class Account(Base):
    __tablename__ = "account"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(String)
    telegram_id = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    time_zone = Column(String)

