from datetime import datetime

from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Boolean, MetaData, BigInteger
from sqlalchemy.orm import relationship

from account.models import Account
from database import Base
from static_key.models import StaticKey

metadata = MetaData()


class Profile(Base):
    __tablename__ = "profile"
    metadata = metadata

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    account_id = Column(BigInteger, ForeignKey(Account.id, ondelete="SET NULL"))

    dynamic_key = Column(String, unique=True)
    static_key_id = Column(BigInteger, ForeignKey(StaticKey.id, ondelete="SET NULL"))

    date_end = Column(TIMESTAMP, default=datetime.utcnow)
    used_bytes = Column(BigInteger)
    is_active = Column(Boolean, default=False)

    account = relationship(Account, backref="profiles", lazy="joined")
    static_key = relationship(StaticKey, backref="profiles", lazy="joined")
