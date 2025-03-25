from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime
from models.model_task import Task
class UserCreate(BaseModel):
    username: str
    email: str
    phone: str
    password: str

class Role(str, Enum):
    admin = "admin"
    user = "user"

class User(UserCreate):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    role: Role = Role.user
    tasks: Optional[List[Task]] = None
    is_active: bool = True
    class Config:
        from_attributes = True


