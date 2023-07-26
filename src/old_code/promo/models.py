from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData

from database import Base
metadata = MetaData()


class Promo(Base):
    __tablename__ = "promo"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
