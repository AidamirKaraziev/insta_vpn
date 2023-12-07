from typing import Optional

from referent_type.schemas import ReferentTypeGet


def getting_referent_type(obj: ReferentTypeGet) -> Optional[ReferentTypeGet]:
    return ReferentTypeGet(
        id=obj.id,
        name=obj.name,
    )
