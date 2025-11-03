from pydantic import BaseModel, EmailStr
from typing import Optional

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    id: int
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str