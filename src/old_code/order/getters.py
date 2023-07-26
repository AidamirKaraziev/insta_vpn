from typing import Optional
from fastapi import Request
from old_code.order.schemas import OrderGet
from old_code.selling_point.getters import getting_selling_point
from old_code.order_status.getters import getting_status
from old_code.cart.getters import getting_cart


def getting_order(obj: OrderGet, request: Optional[Request]) -> Optional[OrderGet]:

    return OrderGet(
        id=obj.id,
        selling_point_id=getting_selling_point(obj.selling_point) if obj.selling_point is not None else None,
        cart=getting_cart(obj=obj.cart, request=request) if obj.cart is not None else None,

        sum=obj.sum,

        created_at=obj.created_at,
        completed_at=obj.completed_at,

        status_id=getting_status(obj.status) if obj.status is not None else None,
        is_active=obj.is_active
    )
