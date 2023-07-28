from datetime import datetime, date
from typing import Optional, Union


def to_timestamp(d: Union[None, datetime, date]) -> Optional[int]:
    if d is None:
        return None
    if isinstance(d, date):
        dt = datetime(year=d.year, month=d.month, day=d.day)
    else:
        dt = d
    result = int(dt.timestamp())
    return result


def date_from_timestamp(ts: Optional[int]) -> Optional[date]:
    if ts is None:
        return None
    return datetime.utcfromtimestamp(ts).date()


def datetime_from_timestamp(ts: Optional[int]) -> Optional[datetime]:
    if ts is None:
        return None
    return datetime.utcfromtimestamp(ts)
