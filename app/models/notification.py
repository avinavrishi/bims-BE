"""
Notification Model - For in-app and email notifications
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enumeration"""
    NEW_APPLICATION = "new_application"
    APPLICATION_APPROVED = "application_approved"
    APPLICATION_REJECTED = "application_rejected"
    MILESTONE_DUE = "milestone_due"
    MILESTONE_APPROVED = "milestone_approved"
    MILESTONE_REJECTED = "milestone_rejected"
    DEAL_ACCEPTED = "deal_accepted"
    PAYMENT_RECEIVED = "payment_received"
    DEAL_POSTED = "deal_posted"  # For influencers when new deals match their profile


class Notification(Base):
    """Notification model"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    notification_type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    
    # Related entities
    related_campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    related_application_id = Column(Integer, ForeignKey("deal_applications.id"), nullable=True)
    related_milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Email notification
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Action URL (for frontend routing)
    action_url = Column(String)
    
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    related_campaign = relationship("Campaign", foreign_keys=[related_campaign_id])
    related_application = relationship("DealApplication", foreign_keys=[related_application_id])
    related_milestone = relationship("Milestone", foreign_keys=[related_milestone_id])

