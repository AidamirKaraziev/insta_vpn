from sqlalchemy import Column, Integer, String, MetaData
from database import Base

metadata = MetaData()


class Status(Base):
    __tablename__ = "order_status"
    metadata = metadata

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
