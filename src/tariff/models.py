from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData

from database import Base
metadata = MetaData()


class Tariff(Base):
    __tablename__ = "tariff"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Integer)
    period_unix = Column(Integer)
    is_active = Column(Boolean, default=True)
