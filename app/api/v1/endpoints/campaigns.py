"""
Campaign Endpoints aligned with UML.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_brand_or_admin, get_current_user
from app.core.database import get_db
from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.user import User, UserRole
from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
)

router = APIRouter()


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_brand_or_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new campaign (brand or admin).
    """
    brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand profile not found for this user.",
        )

    new_campaign = Campaign(
        brand_id=brand.id,
        **campaign_data.dict(),
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List campaigns with role-based visibility:
    - Creators: see all campaigns.
    - Admins: see all campaigns.
    - Brands: see only their own campaigns.
    """
    query = db.query(Campaign)

    if current_user.role == UserRole.BRAND:
        brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
        if not brand:
            return []
        query = query.filter(Campaign.brand_id == brand.id)
    # Creators and Admins see all campaigns; no extra filter needed

    campaigns = query.offset(skip).limit(limit).all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_brand_or_admin),
    db: Session = Depends(get_db),
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
    if not brand or campaign.brand_id != brand.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this campaign",
        )

    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)

    db.commit()
    db.refresh(campaign)
    return campaign

