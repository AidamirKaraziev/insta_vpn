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

    key_id = Column(Integer)
    name = Column(String)
    port = Column(Integer)
    method = Column(String)
    access_url = Column(String)
    used_bytes = Column(Integer)
    data_limit = Column(Integer)

    date_end = Column(TIMESTAMP(timezone=True), default=datetime.utcnow())
    is_active = Column(Boolean, default=False)

    account = relationship(Account, backref="profiles", lazy="joined")
    server = relationship(Server, backref="profiles", lazy="joined")
    __table_args__ = (UniqueConstraint("server_id", "key_id",
                                       name='_server_key_uc'),
                      )
