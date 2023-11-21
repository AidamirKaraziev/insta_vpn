from typing import Optional

from status.schemas import StatusGet


def getting_status(obj: StatusGet) -> Optional[StatusGet]:
    return StatusGet(
        id=obj.id,
        name=obj.name,
    )
