from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData, DateTime, Date, \
    UniqueConstraint
from sqlalchemy.orm import relationship

from account.models import Account
from database import Base
from ip_address.models import IpAddress


metadata = MetaData()


class Profile(Base):
    __tablename__ = "profile"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey(Account.id, ondelete="SET NULL"))
    ip_address_id = Column(Integer, ForeignKey(IpAddress.id, ondelete="SET NULL"))
    peer_name = Column(String, unique=True)
    date_end = Column(Date, default=datetime.today())
    created_at = Column(Date, default=datetime.today())
    is_active = Column(Boolean, default=True)

    account = relationship(Account, backref="profiles", lazy="joined")
    ip_address = relationship(IpAddress, backref="profiles", lazy="joined")

    __table_args__ = (UniqueConstraint("account_id", "ip_address_id", "peer_name",
                                       name='_account_ip_address_peer_name_uc'),
                      )
