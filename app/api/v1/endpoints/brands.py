"""
Brand Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.brand import Brand
from app.models.user import User
from app.schemas.brand import BrandCreate, BrandResponse, BrandUpdate
from app.api.v1.dependencies import get_current_brand_user

router = APIRouter()


@router.post("", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand_data: BrandCreate,
    current_user: User = Depends(get_current_brand_user),
    db: Session = Depends(get_db)
):
    """Create a brand profile"""
    # Check if brand profile already exists
    existing_brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
    if existing_brand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand profile already exists for this user"
        )
    
    new_brand = Brand(**brand_data.dict(), user_id=current_user.id)
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    
    return new_brand


@router.get("/me", response_model=BrandResponse)
async def get_my_brand(
    current_user: User = Depends(get_current_brand_user),
    db: Session = Depends(get_db)
):
    """Get current user's brand profile"""
    brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand profile not found"
        )
    return brand


@router.put("/me", response_model=BrandResponse)
async def update_my_brand(
    brand_data: BrandUpdate,
    current_user: User = Depends(get_current_brand_user),
    db: Session = Depends(get_db)
):
    """Update current user's brand profile"""
    brand = db.query(Brand).filter(Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand profile not found"
        )
    
    update_data = brand_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)
    
    db.commit()
    db.refresh(brand)
    
    return brand


@router.get("", response_model=List[BrandResponse])
async def list_brands(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all brands (for discovery)"""
    brands = db.query(Brand).offset(skip).limit(limit).all()
    return brands


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(brand_id: int, db: Session = Depends(get_db)):
    """Get a specific brand by ID"""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    return brand

