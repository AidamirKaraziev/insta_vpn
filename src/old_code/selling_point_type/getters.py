from typing import Optional
from old_code.selling_point_type.schemas import SellingPointTypeGet


def getting_selling_point_type(obj: SellingPointTypeGet) -> Optional[SellingPointTypeGet]:

    return SellingPointTypeGet(
        id=obj.id,
        name=obj.name,
        is_active=obj.is_active
    )
