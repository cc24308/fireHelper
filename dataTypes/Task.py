from pydantic import BaseModel

class Task(BaseModel):
    name : str
    difficult : int
    type : str
    timed : str
    xp : int
