"""
Campaign Schemas aligned with UML.
"""
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from app.models.campaign import CampaignStatus, CampaignContentType


class CampaignBase(BaseModel):
    title: str
    category: Optional[str] = None
    content_type: CampaignContentType
    description: Optional[str] = None
    total_budget: float
    rate_per_million_views: float
    max_submissions_per_account: Optional[int] = None
    max_earnings_per_creator: Optional[float] = None
    max_earnings_per_post: Optional[float] = None
    start_date: date
    end_date: date
    logo_drive_link: Optional[str] = None
    guidelines_link: Optional[str] = None
    discord_link: Optional[str] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    content_type: Optional[CampaignContentType] = None
    description: Optional[str] = None
    total_budget: Optional[float] = None
    used_budget: Optional[float] = None
    rate_per_million_views: Optional[float] = None
    max_submissions_per_account: Optional[int] = None
    max_earnings_per_creator: Optional[float] = None
    max_earnings_per_post: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[CampaignStatus] = None
    logo_drive_link: Optional[str] = None
    guidelines_link: Optional[str] = None
    discord_link: Optional[str] = None


class CampaignResponse(CampaignBase):
    id: str
    brand_id: str
    status: CampaignStatus
    used_budget: float
    created_at: datetime

    class Config:
        from_attributes = True

