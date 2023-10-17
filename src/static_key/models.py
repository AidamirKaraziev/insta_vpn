from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean, MetaData, UniqueConstraint, BigInteger
from sqlalchemy.orm import relationship

from database import Base
from server.models import Server

metadata = MetaData()


class StaticKey(Base):
    __tablename__ = "static_key"

    metadata = metadata
    id = Column(BigInteger, primary_key=True)
    server_id = Column(Integer, ForeignKey(Server.id, ondelete="SET NULL"))

    key_id = Column(Integer)
    name = Column(String)
    port = Column(Integer)
    method = Column(String)
    access_url = Column(String)
    used_bytes = Column(Integer)
    data_limit = Column(Integer)
    password = Column(String)

    is_active = Column(Boolean, default=False)

    server = relationship(Server, backref="static_keys", lazy="joined")
    __table_args__ = (
        UniqueConstraint("server_id", "key_id", name='_key_server_uc'),
                      )
