"""
API v1 Router - Main router that includes all endpoint routers
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, brands, influencers, campaigns, tasks, content

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(brands.router, prefix="/brands", tags=["Brands"])
api_router.include_router(influencers.router, prefix="/influencers", tags=["Influencers"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(content.router, prefix="/content", tags=["Content"])

