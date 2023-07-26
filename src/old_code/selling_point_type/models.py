from sqlalchemy import Column, Integer, String, MetaData, Boolean
from database import Base

metadata = MetaData()


class SellingPointType(Base):
    __tablename__ = "selling_point_type"
    metadata = metadata

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
