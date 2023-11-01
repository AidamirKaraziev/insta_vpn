from sqlalchemy import Column, Integer, String, Boolean, MetaData
from database import Base

metadata = MetaData()


class VlessKey(Base):
    __tablename__ = "vless_key"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    server_ip = Column(String)
    is_active = Column(Boolean, default=True)
