"""
Content Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.content import Content
from app.models.task import Task
from app.models.influencer import Influencer
from app.models.user import User
from app.schemas.content import ContentCreate, ContentResponse, ContentUpdate
from app.api.v1.dependencies import get_current_user, get_current_influencer_user

router = APIRouter()


@router.post("/task/{task_id}", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    task_id: int,
    content_data: ContentCreate,
    current_user: User = Depends(get_current_influencer_user),
    db: Session = Depends(get_db)
):
    """Create content submission for a task (influencer only)"""
    # Verify task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify influencer owns the task
    influencer = db.query(Influencer).filter(Influencer.user_id == current_user.id).first()
    if task.influencer_id != influencer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to submit content for this task"
        )
    
    # Check if content already exists
    existing_content = db.query(Content).filter(Content.task_id == task_id).first()
    if existing_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content already exists for this task. Use update endpoint instead."
        )
    
    content_dict = content_data.dict()
    content_dict["task_id"] = task_id
    
    new_content = Content(**content_dict)
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    
    return new_content


@router.get("/task/{task_id}", response_model=ContentResponse)
async def get_content_by_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get content for a specific task"""
    content = db.query(Content).filter(Content.task_id == task_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found for this task"
        )
    return content


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific content by ID"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_data: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update content (influencer can update, brand can review)"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    update_data = content_data.dict(exclude_unset=True)
    
    # If brand is reviewing/approving
    if current_user.role.value == "brand" and "status" in update_data:
        update_data["reviewer_id"] = current_user.id
        from datetime import datetime
        update_data["reviewed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(content, field, value)
    
    db.commit()
    db.refresh(content)
    
    return content

