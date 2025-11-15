"""
Brand Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Brand(Base):
    """Brand profile model"""
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String, nullable=False)
    industry = Column(String)
    description = Column(Text)
    website = Column(String)
    logo_url = Column(String)
    location = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    extra_data = Column(JSON, default={})  # For additional brand-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="brand_profile")
    campaigns = relationship("Campaign", back_populates="brand", cascade="all, delete-orphan")

