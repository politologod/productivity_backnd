from pydantic import BaseModel, EmailStr, field_validator, Annotated, StringConstraints
from typing import List, Optional
from enum import Enum
from datetime import datetime
from models.model_task import Task



class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone: str
    password: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not 3 <= len(v.strip()) <= 50:
            raise ValueError('El nombre de usuario debe tener entre 3 y 50 caracteres')
        return v.strip()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        import re
        if not re.match(r'^\+?1?\d{9,15}$', v.strip()):
            raise ValueError('Formato de teléfono inválido')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not 8 <= len(v) <= 100:
            raise ValueError('La contraseña debe tener entre 8 y 100 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(char.islower() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not any(char in '!@#$%^&*()' for char in v):
            raise ValueError('La contraseña debe contener al menos un carácter especial (!@#$%^&*())')
        return v

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


