from sqlalchemy import Column, Integer, String, MetaData
from database import Base

metadata = MetaData()


class PaymentType(Base):
    __tablename__ = "payment_type"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
