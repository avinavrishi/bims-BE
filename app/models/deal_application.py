"""
Deal Application Model - For influencer applications to deals
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ApplicationStatus(str, enum.Enum):
    """Application status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    NEGOTIATING = "negotiating"  # Phase 1.5


class DealApplication(Base):
    """Deal application model - Influencer applies to deal"""
    __tablename__ = "deal_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False)
    
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    
    # Application Details
    proposal_text = Column(Text)  # Influencer's proposal/notes
    quoted_amount = Column(Float, nullable=True)  # If budget is negotiable
    rate_card_url = Column(String)  # Link to influencer's rate card
    
    # Portfolio/Media
    portfolio_items = Column(JSON, default=[])  # Array of portfolio URLs/media
    
    # Review Details
    reviewed_at = Column(DateTime(timezone=True))
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Brand user who reviewed
    rejection_reason = Column(Text)
    notes = Column(Text)  # Internal notes from brand
    
    # Engagement metrics at time of application (for brand review)
    engagement_rate_at_application = Column(Float)
    follower_count_at_application = Column(Integer)
    
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="applications")
    influencer = relationship("Influencer", back_populates="applications")

