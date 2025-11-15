"""
Brand Schemas
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any


class BrandBase(BaseModel):
    """Base brand schema"""
    company_name: str
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None


class BrandCreate(BrandBase):
    """Schema for brand creation"""
    pass


class BrandUpdate(BaseModel):
    """Schema for brand update"""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class BrandResponse(BrandBase):
    """Schema for brand response"""
    id: int
    user_id: int
    logo_url: Optional[str] = None
    extra_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

