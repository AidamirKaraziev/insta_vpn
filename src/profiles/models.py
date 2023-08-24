from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData, DateTime, Date, \
    UniqueConstraint
from sqlalchemy.orm import relationship

from account.models import Account
from database import Base
from server.models import Server

metadata = MetaData()


class Profile(Base):
    __tablename__ = "profile"

    metadata = metadata
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey(Account.id, ondelete="SET NULL"))
    server_id = Column(Integer, ForeignKey(Server.id, ondelete="SET NULL"))
    peer_name = Column(String, unique=True)
    date_end = Column(Date, default=datetime.today())
    # created_at = Column(Date, default=datetime.today())
    is_active = Column(Boolean, default=True)

    account = relationship(Account, backref="profiles", lazy="joined")
    server = relationship(Server, backref="profiles", lazy="joined")
    wg_id = Column(String)
    name = Column(String)
    address = Column(String)
    public_key = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    persistent_keepa_live = Column(String)
    latest_handshake_at = Column(String)

    __table_args__ = (UniqueConstraint("account_id", "server_id", "peer_name",
                                       name='_account_server_peer_name_uc'),
                      )
