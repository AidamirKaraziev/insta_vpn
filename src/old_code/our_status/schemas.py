from pydantic import BaseModel


class StatusGet(BaseModel):
    id: int
    name: str


class StatusCreate(BaseModel):
    pass


class StatusUpdate(BaseModel):
    pass
