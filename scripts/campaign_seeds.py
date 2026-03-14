"""
Seed a sample brand (and its user) and campaigns into the database.

Run from project root: python scripts/campaign_seeds.py
"""

from datetime import date, timedelta

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.campaign import (
    Campaign,
    CampaignStatus,
    CampaignContentType,
)
from app.models.brand import Brand
from app.models.user import User, UserRole, UserStatus
from app.models.profile import Profile, Creator, CreatorVerificationStatus


# Seed brand user + brand (created if not present)
SEED_BRAND_EMAIL = "brand1@gmail.com"
SEED_BRAND_PASSWORD = "Brand@123"  # for dev only; change in production
SEED_COMPANY_NAME = "Demo Brand Co"
SEED_INDUSTRY = "Technology"
SEED_WEBSITE = "https://demobrand.example.com"

# Seed creator user (User + Profile + Creator)
SEED_CREATOR_EMAIL = "user1@gmail.com"
SEED_CREATOR_PASSWORD = "Fuck1@Society"  # for dev only
SEED_CREATOR_DISPLAY_NAME = "Demo Creator"


def get_or_create_seed_brand(db):
    """
    Return a brand to use for seeding. Creates a BRAND user and Brand if none exist.
    """
    # Prefer existing brand with our seed email
    user = db.query(User).filter(User.email == SEED_BRAND_EMAIL).first()
    if user:
        brand = db.query(Brand).filter(Brand.user_id == user.id).first()
        if brand:
            return brand
        # User exists but no brand (shouldn't happen)
        brand = Brand(
            user_id=user.id,
            company_name=SEED_COMPANY_NAME,
            industry=SEED_INDUSTRY,
            website=SEED_WEBSITE,
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand

    # Create brand user + brand
    user = User(
        email=SEED_BRAND_EMAIL,
        password_hash=get_password_hash(SEED_BRAND_PASSWORD),
        role=UserRole.BRAND,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    db.flush()

    brand = Brand(
        user_id=user.id,
        company_name=SEED_COMPANY_NAME,
        industry=SEED_INDUSTRY,
        website=SEED_WEBSITE,
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)
    print(f"✅ Created brand user and brand: {SEED_COMPANY_NAME} ({SEED_BRAND_EMAIL})")
    return brand


def get_or_create_seed_creator(db):
    """
    Return a creator user for seeding. Creates User + Profile + Creator if not present.
    """
    user = db.query(User).filter(User.email == SEED_CREATOR_EMAIL).first()
    if user:
        creator = db.query(Creator).filter(Creator.user_id == user.id).first()
        if creator:
            return creator
        # User exists but no Profile/Creator
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        if not profile:
            profile = Profile(user_id=user.id, display_name=SEED_CREATOR_DISPLAY_NAME)
            db.add(profile)
            db.flush()
        creator = Creator(
            user_id=user.id,
            total_earnings=0.0,
            wallet_balance=0.0,
            verification_status=CreatorVerificationStatus.PENDING,
        )
        db.add(creator)
        db.commit()
        db.refresh(creator)
        print(f"✅ Created Profile + Creator for existing user: {SEED_CREATOR_EMAIL}")
        return creator

    user = User(
        email=SEED_CREATOR_EMAIL,
        password_hash=get_password_hash(SEED_CREATOR_PASSWORD),
        role=UserRole.CREATOR,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    db.flush()

    profile = Profile(user_id=user.id, display_name=SEED_CREATOR_DISPLAY_NAME)
    creator = Creator(
        user_id=user.id,
        total_earnings=0.0,
        wallet_balance=0.0,
        verification_status=CreatorVerificationStatus.PENDING,
    )
    db.add(profile)
    db.add(creator)
    db.commit()
    db.refresh(creator)
    print(f"✅ Created creator user: {SEED_CREATOR_DISPLAY_NAME} ({SEED_CREATOR_EMAIL})")
    return creator


def seed_campaigns():
    db = SessionLocal()
    try:
        # --------------------------------------------------
        # Get or create the seed brand and seed creator
        # --------------------------------------------------
        brand = get_or_create_seed_brand(db)
        get_or_create_seed_creator(db)

        # --------------------------------------------------
        # Check if campaigns already exist for this brand
        # --------------------------------------------------
        existing = db.query(Campaign).filter(Campaign.brand_id == brand.id).count()
        if existing > 0:
            print("ℹ️ Campaigns already exist for this brand. Skipping campaign seeding.")
            return

        today = date.today()

        campaigns = [
            Campaign(
                brand_id=brand.id,
                title="BetStrike [GENERAL - VIDEO]",
                category="GENERAL",
                content_type=CampaignContentType.VIDEO,
                description="Create English short-form videos promoting BetStrike.",
                total_budget=2000.0,
                used_budget=0.0,
                rate_per_million_views=30.0,
                max_submissions_per_account=50,
                max_earnings_per_creator=1500.0,
                max_earnings_per_post=90.0,
                start_date=today,
                end_date=today + timedelta(days=30),
                status=CampaignStatus.ACTIVE,
                logo_drive_link="https://drive.google.com/example-logo",
                guidelines_link="https://notion.so/example-guidelines",
                discord_link="https://discord.gg/example",
            ),
            Campaign(
                brand_id=brand.id,
                title="CryptoPlay Reels Campaign",
                category="CRYPTO",
                content_type=CampaignContentType.VIDEO,
                description="Instagram Reels & TikTok videos for CryptoPlay app.",
                total_budget=5000.0,
                used_budget=0.0,
                rate_per_million_views=45.0,
                max_submissions_per_account=20,
                max_earnings_per_creator=2000.0,
                max_earnings_per_post=120.0,
                start_date=today,
                end_date=today + timedelta(days=45),
                status=CampaignStatus.ACTIVE,
            ),
            Campaign(
                brand_id=brand.id,
                title="ShopEase Product Image Campaign",
                category="E-COMMERCE",
                content_type=CampaignContentType.IMAGE,
                description="Post product images showcasing ShopEase deals.",
                total_budget=1000.0,
                used_budget=0.0,
                rate_per_million_views=20.0,
                max_submissions_per_account=10,
                max_earnings_per_creator=500.0,
                max_earnings_per_post=50.0,
                start_date=today - timedelta(days=10),
                end_date=today + timedelta(days=10),
                status=CampaignStatus.ACTIVE,
            ),
        ]

        db.add_all(campaigns)
        db.commit()

        print(f"✅ Seeded {len(campaigns)} campaigns under brand '{brand.company_name}'.")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding campaigns:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_campaigns()
