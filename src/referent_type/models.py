from sqlalchemy import Column, Integer, String, MetaData
from database import Base

metadata = MetaData()


class ReferentType(Base):
    __tablename__ = "referent_type"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
