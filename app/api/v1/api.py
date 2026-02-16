"""
API v1 Router - includes UML-relevant routers
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, campaigns, admin, profiles

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])

