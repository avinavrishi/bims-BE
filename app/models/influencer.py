"""
Influencer Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Influencer(Base):
    """Influencer profile model"""
    __tablename__ = "influencers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    bio = Column(Text)
    niche = Column(String)  # e.g., "fashion", "tech", "lifestyle"
    location = Column(String)
    profile_picture_url = Column(String)
    
    # Social Media Links
    instagram_handle = Column(String)
    youtube_handle = Column(String)
    tiktok_handle = Column(String)
    twitter_handle = Column(String)
    
    # Metrics (can be synced from APIs later)
    total_followers = Column(Integer, default=0)
    average_engagement_rate = Column(Float, default=0.0)
    
    # Portfolio and extra data
    portfolio_url = Column(String)
    previous_campaigns = Column(JSON, default=[])  # List of previous campaign IDs or details
    extra_data = Column(JSON, default={})  # For additional influencer-specific data
    
    # Pricing
    base_rate = Column(Float)  # Base rate per post/campaign
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Saved deals (Phase 1)
    saved_deals = Column(JSON, default=[])  # Array of campaign IDs that influencer saved
    
    # Relationships
    user = relationship("User", back_populates="influencer_profile")
    campaign_participations = relationship("Campaign", back_populates="influencer", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="influencer", cascade="all, delete-orphan")
    applications = relationship("DealApplication", back_populates="influencer", cascade="all, delete-orphan")

