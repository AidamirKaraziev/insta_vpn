from typing import Optional
from fastapi import Request
from old_code.cart.schemas import CartGet
from old_code.dish.getters import getting_dish


def getting_cart(obj: CartGet, request: Optional[Request]) -> Optional[CartGet]:

    return CartGet(
        id=obj.id,
        order_id=obj.order_id,
        dish_id=getting_dish(obj.dish, request) if obj.dish is not None else None,
        quantity=obj.quantity,
        sum=obj.sum,
    )
