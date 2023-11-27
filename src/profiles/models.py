import uuid
from datetime import datetime

from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Boolean, MetaData, BigInteger, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base

from account.models import Account
from outline_key.models import OutlineKey

metadata = MetaData()


class Profile(Base):
    __tablename__ = "profile"
    metadata = metadata

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    account_id = Column(BigInteger, ForeignKey(Account.id, ondelete="SET NULL"))

    outline_key_id = Column(BigInteger, ForeignKey(OutlineKey.id, ondelete="SET NULL"), unique=True)
    # vless_link = Column(String)
    # vless_key_id = Column(Integer, ForeignKey(VlessKey.id, ondelete="SET NULL"), unique=True)

    date_end = Column(TIMESTAMP, default=datetime.utcnow)
    used_bytes = Column(BigInteger)

    is_active = Column(Boolean, default=False)

    account = relationship(Account, backref="profiles", lazy="joined")
    outline_key = relationship(OutlineKey, backref="profiles", lazy="joined")
