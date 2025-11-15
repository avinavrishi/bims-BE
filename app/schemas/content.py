"""
Content Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.content import ContentStatus, ContentType


class ContentBase(BaseModel):
    """Base content schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    platform: Optional[str] = None


class ContentCreate(ContentBase):
    """Schema for content creation"""
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    additional_files: Optional[List[str]] = None


class ContentUpdate(BaseModel):
    """Schema for content update"""
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    status: Optional[ContentStatus] = None
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    additional_files: Optional[List[str]] = None
    platform: Optional[str] = None
    post_url: Optional[str] = None
    review_notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class ContentResponse(ContentBase):
    """Schema for content response"""
    id: int
    task_id: int
    status: ContentStatus
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    additional_files: List[str] = []
    post_url: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None
    extra_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

