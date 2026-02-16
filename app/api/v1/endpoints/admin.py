"""
Admin endpoints for managing users, brands, and KPIs.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.brand import Brand
from app.models.campaign import Campaign, CampaignStatus
from app.models.economy import Payout
from app.schemas.user import UserResponse

router = APIRouter()


def _require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# ==== USER MANAGEMENT ====


@router.get("/users", response_model=List[UserResponse])
async def admin_list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    return db.query(User).all()


@router.get("/users/{user_id}", response_model=UserResponse)
async def admin_get_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    db.delete(user)
    db.commit()
    return None


# ==== BRAND MANAGEMENT ====


from pydantic import BaseModel

class BrandAdminResponseModel(BaseModel):
    id: str
    user_id: str
    company_name: str
    industry: str | None = None
    website: str | None = None


class BrandAdminCreate(BaseModel):
    user_id: str
    company_name: str
    industry: str | None = None
    website: str | None = None


class BrandAdminUpdate(BaseModel):
    company_name: str | None = None
    industry: str | None = None
    website: str | None = None


@router.get("/brands", response_model=List[BrandAdminResponseModel])
async def admin_list_brands(
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    return db.query(Brand).all()


@router.post(
    "/brands",
    response_model=BrandAdminResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def admin_create_brand(
    data: BrandAdminCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    # Ensure user exists and is a BRAND
    brand_user = db.query(User).filter(User.id == data.user_id).first()
    if not brand_user or brand_user.role != UserRole.BRAND:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided user_id must belong to a BRAND user",
        )

    existing = db.query(Brand).filter(Brand.user_id == data.user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand already exists for this user",
        )

    brand = Brand(
        user_id=data.user_id,
        company_name=data.company_name,
        industry=data.industry,
        website=data.website,
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


@router.get("/brands/{brand_id}", response_model=BrandAdminResponseModel)
async def admin_get_brand(
    brand_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    return brand


@router.patch("/brands/{brand_id}", response_model=BrandAdminResponseModel)
async def admin_update_brand(
    brand_id: str,
    data: BrandAdminUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)

    db.commit()
    db.refresh(brand)
    return brand


@router.delete("/brands/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_brand(
    brand_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    db.delete(brand)
    db.commit()
    return None


# ==== KPIs ====


class AdminKPIResponse(BaseModel):
    total_users: int
    total_creators: int
    total_brands: int
    total_admins: int
    total_campaigns: int
    active_campaigns: int
    paused_campaigns: int
    completed_campaigns: int
    total_payout_amount: float


@router.get("/kpis", response_model=AdminKPIResponse)
async def admin_kpis(
    db: Session = Depends(get_db),
    admin: User = Depends(_require_admin),
):
    from app.models.user import UserRole as UR

    total_users = db.query(User).count()
    total_creators = db.query(User).filter(User.role == UR.CREATOR).count()
    total_brands = db.query(User).filter(User.role == UR.BRAND).count()
    total_admins = db.query(User).filter(User.role == UR.ADMIN).count()

    total_campaigns = db.query(Campaign).count()
    active_campaigns = db.query(Campaign).filter(Campaign.status == CampaignStatus.ACTIVE).count()
    paused_campaigns = db.query(Campaign).filter(Campaign.status == CampaignStatus.PAUSED).count()
    completed_campaigns = db.query(Campaign).filter(Campaign.status == CampaignStatus.COMPLETED).count()

    total_payout_amount = (
        db.query(Payout)
        .with_entities(func.coalesce(func.sum(Payout.amount), 0.0))
        .scalar()
    )

    return AdminKPIResponse(
        total_users=total_users,
        total_creators=total_creators,
        total_brands=total_brands,
        total_admins=total_admins,
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        paused_campaigns=paused_campaigns,
        completed_campaigns=completed_campaigns,
        total_payout_amount=total_payout_amount,
    )

