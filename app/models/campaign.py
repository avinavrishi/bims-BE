"""
Campaign Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign(Base):
    """Campaign/Deal model - Phase 1 MVP"""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=True)  # Nullable for open deals
    posted_by_admin = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin can post on behalf of brand
    
    title = Column(String, nullable=False)
    description = Column(Text)
    brief = Column(Text)  # Campaign brief/requirements
    
    # Deal Details (Phase 1)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    budget = Column(Float, nullable=False)  # Total budget
    budget_negotiable = Column(String, default="fixed")  # "fixed" or "negotiable"
    deadline = Column(DateTime(timezone=True), nullable=False)  # Application deadline
    required_follower_count = Column(Integer, nullable=True)  # Optional minimum followers
    
    # Platforms (Instagram, TikTok, YouTube, etc.)
    platforms = Column(JSON, default=[])  # ["instagram", "tiktok", "youtube"]
    
    # Deliverables
    deliverables = Column(JSON, default=[])  # List of deliverables required
    
    # Milestones structure (Phase 1)
    # Format: [{"title": "Concept submission", "payout_percentage": 20}, ...]
    milestones_template = Column(JSON, default=[])  # Template for milestones
    
    # Campaign Dates
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    # Requirements (legacy fields, kept for compatibility)
    required_deliverables = Column(JSON, default=[])  # List of required content types
    target_audience = Column(JSON, default={})  # Target audience demographics
    content_guidelines = Column(Text)
    
    # Performance Metrics (can be updated via API integrations)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Trending/Discovery fields
    is_trending = Column(String, default="false")  # For trending deals
    view_count = Column(Integer, default=0)  # For discovery ranking
    application_count = Column(Integer, default=0)  # Number of applications
    
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="campaigns")
    influencer = relationship("Influencer", back_populates="campaign_participations")
    tasks = relationship("Task", back_populates="campaign", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="campaign", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="campaign", cascade="all, delete-orphan")
    applications = relationship("DealApplication", back_populates="campaign", cascade="all, delete-orphan")

