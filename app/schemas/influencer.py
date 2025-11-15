"""
Influencer Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List


class InfluencerBase(BaseModel):
    """Base influencer schema"""
    full_name: str
    bio: Optional[str] = None
    niche: Optional[str] = None
    location: Optional[str] = None
    instagram_handle: Optional[str] = None
    youtube_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    twitter_handle: Optional[str] = None


class InfluencerCreate(InfluencerBase):
    """Schema for influencer creation"""
    base_rate: Optional[float] = None


class InfluencerUpdate(BaseModel):
    """Schema for influencer update"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    niche: Optional[str] = None
    location: Optional[str] = None
    profile_picture_url: Optional[str] = None
    instagram_handle: Optional[str] = None
    youtube_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    twitter_handle: Optional[str] = None
    total_followers: Optional[int] = None
    average_engagement_rate: Optional[float] = None
    portfolio_url: Optional[str] = None
    base_rate: Optional[float] = None
    extra_data: Optional[Dict[str, Any]] = None


class InfluencerResponse(InfluencerBase):
    """Schema for influencer response"""
    id: int
    user_id: int
    profile_picture_url: Optional[str] = None
    total_followers: int = 0
    average_engagement_rate: float = 0.0
    portfolio_url: Optional[str] = None
    previous_campaigns: List[Any] = []
    base_rate: Optional[float] = None
    extra_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

