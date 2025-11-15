"""
Message Model - For direct and group messaging
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Message(Base):
    """Message model for communication between brands and influencers"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for group messages
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)  # For campaign-specific chats
    
    subject = Column(String)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    is_group_message = Column(Boolean, default=False)
    
    # Attachments
    attachments = Column(JSON, default=[])  # Array of file URLs
    
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

