"""
Task Model - For Kanban-style task management
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TaskStatus(str, enum.Enum):
    """Task status enumeration (Kanban board columns)"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class TaskPriority(str, enum.Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    """Task model for campaign task management"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # Task Details
    due_date = Column(DateTime(timezone=True))
    deliverable_type = Column(String)  # e.g., "instagram_post", "youtube_video", "blog_post"
    requirements = Column(Text)
    
    # Position for Kanban board
    position = Column(Integer, default=0)  # For drag-and-drop ordering
    
    # Review and Approval
    submitted_at = Column(DateTime(timezone=True))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="tasks")
    influencer = relationship("Influencer", back_populates="tasks")
    content = relationship("Content", back_populates="task", uselist=False, cascade="all, delete-orphan")

