"""
Content Model - For influencer content submissions
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ContentStatus(str, enum.Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class ContentType(str, enum.Enum):
    """Content type enumeration"""
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    LINK = "link"
    OTHER = "other"


class Content(Base):
    """Content model for influencer submissions"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), unique=True, nullable=False)
    
    title = Column(String)
    description = Column(Text)
    content_type = Column(Enum(ContentType))
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    
    # File URLs
    file_url = Column(String)  # Main content file
    thumbnail_url = Column(String)  # Thumbnail/preview
    additional_files = Column(JSON, default=[])  # Array of additional file URLs
    
    # Social Media Details
    platform = Column(String)  # instagram, youtube, tiktok, etc.
    post_url = Column(String)  # URL to published post (if applicable)
    
    # Review
    review_notes = Column(Text)
    reviewed_at = Column(DateTime(timezone=True))
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="content")

