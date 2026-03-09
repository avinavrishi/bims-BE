"""
Seed sample campaigns into the database
"""

from datetime import date, timedelta

from app.core.database import SessionLocal
from app.models.campaign import (
    Campaign,
    CampaignStatus,
    CampaignContentType,
)
from app.models.brand import Brand


def seed_campaigns():
    db = SessionLocal()
    try:
        # --------------------------------------------------
        # Fetch existing brands (must exist first)
        # --------------------------------------------------
        brands = db.query(Brand).all()

        if not brands:
            print("❌ No brands found. Please create brands first.")
            return

        # Use first brand for demo
        brand = brands[0]

        # --------------------------------------------------
        # Check if campaigns already exist
        # --------------------------------------------------
        existing = db.query(Campaign).count()
        if existing > 0:
            print("ℹ️ Campaigns already exist. Skipping seeding.")
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

        print(f"✅ Seeded {len(campaigns)} campaigns successfully.")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding campaigns:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_campaigns()
