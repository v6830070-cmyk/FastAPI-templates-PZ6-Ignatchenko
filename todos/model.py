from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    name: str
    email: str

class Todo(BaseModel):
    id: int
    user_email: str
    item: str

# Модель для Swagger (теперь просит и имя, и email)
class TaskCreate(BaseModel):
    item: str
    user_name: str
    user_email: str