"""
Profile schemas (public identity layer).
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProfileBase(BaseModel):
    display_name: str
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    country: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    country: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

