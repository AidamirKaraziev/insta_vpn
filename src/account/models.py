from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData
from database import Base


metadata = MetaData()


class Account(Base):
    __tablename__ = "account"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(String, unique=True)
    telegram_id = Column(Integer, unique=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow())
    time_zone = Column(String)
