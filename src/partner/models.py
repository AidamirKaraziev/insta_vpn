from sqlalchemy import Column, Integer, String, MetaData
from database import Base

metadata = MetaData()


class Partner(Base):
    __tablename__ = "partner"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
