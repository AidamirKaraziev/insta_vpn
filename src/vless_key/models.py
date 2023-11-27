from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, MetaData
from sqlalchemy.orm import relationship

from server.models import Server

metadata = MetaData()


class VlessKey(Base):
    __tablename__ = "vless_key"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    server_id = Column(Integer, ForeignKey(Server.id, ondelete="CASCADE"))
    is_active = Column(Boolean, default=True)

    server = relationship(Server, backref="vless_keys", lazy="joined")
