"""
Brandfluence - Brand-Influencer Collaboration Platform
Main FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, check_db_exists
from app.api.v1.api import api_router
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Brandfluence API",
    description="Brand-Influencer Collaboration Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on server startup
    Creates all tables if they don't exist (works for both SQLite and PostgreSQL)
    """
    try:
        logger.info("Initializing database...")
        init_db()
        
        # Check if database exists (for logging purposes)
        db_exists = check_db_exists()
        if db_exists:
            logger.info("Database initialized successfully - tables created/verified")
        else:
            logger.info("Database file created and initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Brandfluence API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

