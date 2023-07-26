from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, MetaData
from sqlalchemy.orm import relationship

from database import Base
from role.models import Role

metadata = MetaData()


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"
    metadata = metadata

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    photo = Column(String, nullable=True)

    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)

    hashed_password: str = Column(String(length=1024), nullable=False)
    role_id = Column(Integer, ForeignKey(Role.id, ondelete="SET NULL"))
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)

    role = relationship(Role, backref="roles", lazy="joined")
