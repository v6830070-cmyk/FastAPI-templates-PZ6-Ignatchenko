from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    name: str
    email: str

class Todo(BaseModel):
    id: int
    user_email: str
    item: str

class TaskCreate(BaseModel):
    item: str
    user_name: str
    user_email: str

# Новая модель: используется только для красивого вывода в Swagger
class TodoResponse(BaseModel):
    id: int
    item: str
    user_name: str
    user_email: str