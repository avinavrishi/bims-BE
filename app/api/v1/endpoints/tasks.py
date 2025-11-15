"""
Task Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.task import Task
from app.models.campaign import Campaign
from app.models.brand import Brand
from app.models.influencer import Influencer
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.api.v1.dependencies import get_current_user, get_current_brand_user

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_brand_user),
    db: Session = Depends(get_db)
):
    """Create a new task (brand only)"""
    # Verify campaign exists and belongs to brand
    campaign = db.query(Campaign).filter(Campaign.id == task_data.campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
    if campaign.brand_id != brand.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create tasks for this campaign"
        )
    
    # Verify influencer exists
    influencer = db.query(Influencer).filter(Influencer.id == task_data.influencer_id).first()
    if not influencer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )
    
    task_dict = task_data.dict()
    # campaign_id is already in task_dict from TaskCreate schema
    
    new_task = Task(**task_dict)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    campaign_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List tasks (filtered by user role and campaign)"""
    query = db.query(Task)
    
    if campaign_id:
        query = query.filter(Task.campaign_id == campaign_id)
    
    if current_user.role.value == "influencer":
        influencer = db.query(Influencer).filter(Influencer.user_id == current_user.id).first()
        if influencer:
            query = query.filter(Task.influencer_id == influencer.id)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify permissions
    if current_user.role.value == "brand":
        brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
        campaign = db.query(Campaign).filter(Campaign.id == task.campaign_id).first()
        if campaign.brand_id != brand.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this task"
            )
    elif current_user.role.value == "influencer":
        influencer = db.query(Influencer).filter(Influencer.user_id == current_user.id).first()
        if task.influencer_id != influencer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this task"
            )
    
    update_data = task_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task

