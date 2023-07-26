from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Boolean, MetaData, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base

from old_code.selling_point.models import SellingPoint
from old_code.order_status.models import Status


metadata = MetaData()


class Order(Base):
    __tablename__ = "order"
    metadata = metadata

    id = Column(Integer, primary_key=True, autoincrement=True)
    selling_point_id = Column(Integer, ForeignKey(SellingPoint.id, ondelete="SET NULL"), nullable=True)
    
    cart = relationship("Cart", back_populates="order", uselist=False, lazy="joined")

    sum = Column(Integer, nullable=False, default=0)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    completed_at = Column(TIMESTAMP, nullable=True)

    status_id = Column(Integer, ForeignKey(Status.id, ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    selling_point = relationship(SellingPoint, backref="orders", lazy="joined")
    status = relationship(Status, backref="orders", lazy="joined")
