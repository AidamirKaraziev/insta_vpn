from sqlalchemy import Column, Integer, String, MetaData
from database import Base

metadata = MetaData()


class Status(Base):
    __tablename__ = "status"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
