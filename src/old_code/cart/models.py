from sqlalchemy import Column, Integer, ForeignKey, Float, MetaData
from sqlalchemy.orm import relationship
from database import Base

from old_code.dish.models import Dish
from old_code.order.models import Order

metadata = MetaData()


class Cart(Base):
    __tablename__ = "cart"
    metadata = metadata

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey(Order.id, ondelete="SET NULL"), nullable=True)
    order = relationship("Order", back_populates="cart", lazy="joined")

    dish_id = Column(Integer, ForeignKey(Dish.id, ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False)
    sum = Column(Float, nullable=False)

    dish = relationship(Dish, backref="carts", lazy="joined")
