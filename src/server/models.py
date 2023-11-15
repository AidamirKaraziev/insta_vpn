from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData
from sqlalchemy.orm import relationship

from database import Base
from vpn_type.models import VpnType

metadata = MetaData()


class Server(Base):
    __tablename__ = "server"

    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=False)
    vpn_type_id = Column(Integer, ForeignKey(VpnType.id, ondelete="SET NULL", onupdate="CASCADE"))
    name = Column(String)
    api_url = Column(String, unique=True)
    cert_sha256 = Column(String)

    marzban_login = Column(String)
    marzban_pass = Column(String)

    address = Column(String, unique=True)
    port = Column(String)
    max_client = Column(Integer)
    fact_client = Column(Integer)

    is_active = Column(Boolean)

    vpn_type = relationship(VpnType, backref="servers", lazy="joined")
