"""
Campaign Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.campaign import Campaign
from app.models.brand import Brand
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.api.v1.dependencies import get_current_user, get_current_brand_user

router = APIRouter()


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_brand_user),
    db: Session = Depends(get_db)
):
    """Create a new campaign (brand only)"""
    # Get brand profile
    brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand profile not found. Please create your brand profile first."
        )
    
    campaign_dict = campaign_data.dict()
    campaign_dict["brand_id"] = brand.id
    
    new_campaign = Campaign(**campaign_dict)
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    
    return new_campaign


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List campaigns (filtered by user role)"""
    if current_user.role.value == "brand":
        brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
        if brand:
            campaigns = db.query(Campaign).filter(Campaign.brand_id == brand.id).offset(skip).limit(limit).all()
        else:
            campaigns = []
    elif current_user.role.value == "influencer":
        from app.models.influencer import Influencer
        influencer = db.query(Influencer).filter(Influencer.user_id == current_user.id).first()
        if influencer:
            campaigns = db.query(Campaign).filter(Campaign.influencer_id == influencer.id).offset(skip).limit(limit).all()
        else:
            campaigns = []
    else:
        campaigns = db.query(Campaign).offset(skip).limit(limit).all()
    
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific campaign by ID"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_brand_user),
    db: Session = Depends(get_db)
):
    """Update a campaign (brand only)"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Verify ownership
    brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
    if campaign.brand_id != brand.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this campaign"
        )
    
    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    
    return campaign

