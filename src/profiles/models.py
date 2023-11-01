import uuid
from datetime import datetime

from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Boolean, MetaData, BigInteger, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from database import Base

from account.models import Account
from shadowsocks_key.models import ShadowsocksKey
from vless_key.models import VlessKey
from vpn_type.models import VpnType

metadata = MetaData()


class Profile(Base):
    __tablename__ = "profile"
    metadata = metadata

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    account_id = Column(BigInteger, ForeignKey(Account.id, ondelete="SET NULL"))

    dynamic_key = Column(String, unique=True)
    shadowsocks_key_id = Column(BigInteger, ForeignKey(ShadowsocksKey.id, ondelete="SET NULL"), unique=True)
    vless_key_id = Column(Integer, ForeignKey(VlessKey.id, ondelete="SET NULL"), unique=True)

    date_end = Column(TIMESTAMP, default=datetime.utcnow)
    used_bytes = Column(BigInteger)
    vpn_type_id = Column(Integer, ForeignKey(VpnType.id, ondelete="SET NULL"))
    is_active = Column(Boolean, default=False)

    account = relationship(Account, backref="profiles", lazy="joined")
    shadowsocks_key = relationship(ShadowsocksKey, backref="profiles", lazy="joined")
    vpn_type = relationship(VpnType, backref="profiles", lazy="joined")
