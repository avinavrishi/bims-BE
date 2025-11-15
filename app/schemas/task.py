"""
Task Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Base task schema"""
    title: str
    description: Optional[str] = None
    deliverable_type: Optional[str] = None
    requirements: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Schema for task creation"""
    campaign_id: int
    influencer_id: int
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskUpdate(BaseModel):
    """Schema for task update"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    deliverable_type: Optional[str] = None
    requirements: Optional[str] = None
    due_date: Optional[datetime] = None
    position: Optional[int] = None
    review_notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    campaign_id: int
    influencer_id: int
    status: TaskStatus
    priority: TaskPriority
    position: int = 0
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    reviewer_id: Optional[int] = None
    extra_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

