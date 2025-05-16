from pydantic import BaseModel

class Task(BaseModel):
    name : str
    difficult : int
    type : str
    xp : int


class User(BaseModel):
    name : str
