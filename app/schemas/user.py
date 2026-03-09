"""
User Schemas aligned with UML.
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    """
    Creator signup schema. Display name/username is asked on first login, not at registration.
    """

    password: str


class BrandUserCreate(UserBase):
    """
    Brand user signup schema (creates USER+BRAND).
    """

    password: str
    company_name: str
    industry: Optional[str] = None
    website: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    username: Optional[str] = None
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPair(Token):
    refresh_token: str
    session_id: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

