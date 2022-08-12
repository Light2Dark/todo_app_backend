from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
    age: int
    
class ToDo(BaseModel):
    id: int
    item: str