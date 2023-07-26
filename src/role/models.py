from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData

from database import Base
metadata = MetaData()


class Role(Base):
    __tablename__ = "role"
    metadata = metadata

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

