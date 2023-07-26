from pydantic import BaseModel


class StatusGet(BaseModel):
    id: int
    name: str


class StatusCreate(BaseModel):
    name: str


class StatusUpdate(BaseModel):
    name: str


