"""
Main FastAPI Application
Entry point for the Loyalty & Reward Program API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.admin_api import router as admin_router
from database import init_db
from config import settings
import logging

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Scalable, Customizable, Profit-Safe Loyalty & Reward Program for Gaming Platforms"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_router, prefix="/api", tags=["Admin"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Loyalty & Reward Program API")
    logger.info(f"Version: {settings.app_version}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    )
