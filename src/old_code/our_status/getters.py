from typing import Optional
from old_code.our_status.schemas import StatusGet


def getting_status(obj: StatusGet) -> Optional[StatusGet]:

    return StatusGet(
        id=obj.id,
        name=obj.name
    )
