"""
Pydantic schemas for authentication & users.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

Role = Literal['admin', 'engineer', 'viewer']


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: Role = 'engineer'


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    name: str
    email: str
    role: Role
    is_active: bool = True
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserPublic
