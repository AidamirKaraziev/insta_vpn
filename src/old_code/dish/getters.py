from fastapi import Request
from typing import Optional
from old_code.dish.schemas import DishGet
from old_code.promo.getters import getting_promo


def getting_dish(obj: DishGet, request: Request) -> Optional[DishGet]:
    if request is not None:
        url = request.url.hostname + ":8000" + "/static/"
        if obj.main_photo is not None:
            obj.main_photo = url + str(obj.main_photo)
        else:
            obj.main_photo = None
        if obj.photo1 is not None:
            obj.photo1 = url + str(obj.photo1)
        else:
            obj.photo1 = None
        if obj.photo2 is not None:
            obj.photo2 = url + str(obj.photo2)
        else:
            obj.photo2 = None

    return DishGet(
        id=obj.id,
        name=obj.name,
        main_photo=obj.main_photo,
        photo1=obj.photo1,
        photo2=obj.photo2,

        description=obj.description,
        composition=obj.composition,
        price=obj.price,

        promo_id=getting_promo(obj.promo) if obj.promo is not None else None,
        is_active=obj.is_active,
        visible=obj.visible,
    )
