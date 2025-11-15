"""
Influencer Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.influencer import Influencer
from app.models.user import User
from app.schemas.influencer import InfluencerCreate, InfluencerResponse, InfluencerUpdate
from app.api.v1.dependencies import get_current_influencer_user

router = APIRouter()


@router.post("", response_model=InfluencerResponse, status_code=status.HTTP_201_CREATED)
async def create_influencer(
    influencer_data: InfluencerCreate,
    current_user: User = Depends(get_current_influencer_user),
    db: Session = Depends(get_db)
):
    """Create an influencer profile"""
    # Check if influencer profile already exists
    existing_influencer = db.query(Influencer).filter(Influencer.user_id == current_user.id).first()
    if existing_influencer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Influencer profile already exists for this user"
        )
    
    new_influencer = Influencer(**influencer_data.dict(), user_id=current_user.id)
    db.add(new_influencer)
    db.commit()
    db.refresh(new_influencer)
    
    return new_influencer


@router.get("/me", response_model=InfluencerResponse)
async def get_my_influencer(
    current_user: User = Depends(get_current_influencer_user),
    db: Session = Depends(get_db)
):
    """Get current user's influencer profile"""
    influencer = db.query(Influencer).filter(Influencer.user_id == current_user.id).first()
    if not influencer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer profile not found"
        )
    return influencer


@router.put("/me", response_model=InfluencerResponse)
async def update_my_influencer(
    influencer_data: InfluencerUpdate,
    current_user: User = Depends(get_current_influencer_user),
    db: Session = Depends(get_db)
):
    """Update current user's influencer profile"""
    influencer = db.query(Influencer).filter(Influencer.user_id == current_user.id).first()
    if not influencer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer profile not found"
        )
    
    update_data = influencer_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(influencer, field, value)
    
    db.commit()
    db.refresh(influencer)
    
    return influencer


@router.get("", response_model=List[InfluencerResponse])
async def list_influencers(
    skip: int = 0,
    limit: int = 100,
    niche: Optional[str] = None,
    min_followers: Optional[int] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all influencers with optional filters (for brand discovery)"""
    query = db.query(Influencer)
    
    if niche:
        query = query.filter(Influencer.niche.ilike(f"%{niche}%"))
    if min_followers:
        query = query.filter(Influencer.total_followers >= min_followers)
    if location:
        query = query.filter(Influencer.location.ilike(f"%{location}%"))
    
    influencers = query.offset(skip).limit(limit).all()
    return influencers


@router.get("/{influencer_id}", response_model=InfluencerResponse)
async def get_influencer(influencer_id: int, db: Session = Depends(get_db)):
    """Get a specific influencer by ID"""
    influencer = db.query(Influencer).filter(Influencer.id == influencer_id).first()
    if not influencer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Influencer not found"
        )
    return influencer

