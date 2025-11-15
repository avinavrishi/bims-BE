"""
Campaign Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.campaign import CampaignStatus


class CampaignBase(BaseModel):
    """Base campaign schema"""
    title: str
    description: Optional[str] = None
    brief: Optional[str] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CampaignCreate(CampaignBase):
    """Schema for campaign creation"""
    influencer_id: Optional[int] = None
    required_deliverables: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None
    content_guidelines: Optional[str] = None


class CampaignUpdate(BaseModel):
    """Schema for campaign update"""
    title: Optional[str] = None
    description: Optional[str] = None
    brief: Optional[str] = None
    status: Optional[CampaignStatus] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    influencer_id: Optional[int] = None
    required_deliverables: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None
    content_guidelines: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class CampaignResponse(CampaignBase):
    """Schema for campaign response"""
    id: int
    brand_id: int
    influencer_id: Optional[int] = None
    status: CampaignStatus
    required_deliverables: List[str] = []
    target_audience: Dict[str, Any] = {}
    content_guidelines: Optional[str] = None
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    engagement_rate: float = 0.0
    extra_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

