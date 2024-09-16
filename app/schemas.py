from typing import List

from pydantic import BaseModel


class Face(BaseModel):
    bounding_box: dict
    gender: str
    age: int


class Image(BaseModel):
    filename: str
    faces: List[Face]


class TaskBase(BaseModel):
    name: str


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    images: List[Image]

    class Config:
        orm_mode = True
