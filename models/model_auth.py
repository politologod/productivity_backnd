from pydantic import BaseModel

class LoginForm(BaseModel):
    email: str
    password: str

class CurrentUser(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool 