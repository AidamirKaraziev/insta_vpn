from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData

from database import Base
metadata = MetaData()


class Server(Base):
    __tablename__ = "server"

    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=True)
    api_url = Column(String, nullable=False, unique=True)
    cert_sha256 = Column(String)
    max_client = Column(Integer)
    fact_client = Column(Integer)
    is_active = Column(Boolean, default=True)
