"""
EduManage Student Management System - FastAPI Backend
Phase 3: MongoDB Database Connection & Health Verification
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.mongodb import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("edumanage.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    Attempts MongoDB connection on startup without crashing if server is offline.
    """
    logger.info("Initializing EduManage API backend...")
    connected = db_manager.connect()
    if connected:
        logger.info("MongoDB connection established successfully.")
    else:
        logger.warning("MongoDB is currently offline. API started in decoupled mode.")

    yield

    # Clean shutdown
    logger.info("Shutting down EduManage API backend...")
    db_manager.close()


# Initialize FastAPI Application with Lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for the EduManage Student Management System with MongoDB support",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS)
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint providing basic API metadata and service endpoints.
    """
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "active",
        "docs": "/docs",
        "health": "/api/health",
        "db_health": "/api/db/health",
        "users": "/api/users",
        "auth_login": "/api/auth/login"
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    """
    FastAPI service health check endpoint.
    """
    return {
        "status": "success",
        "message": "EduManage API is running"
    }


@app.get("/api/db/health", tags=["Database"])
def db_health_check(response: Response):
    """
    MongoDB database connectivity verification endpoint.
    Returns success if MongoDB responds, or error details if unavailable.
    """
    result = db_manager.ping()
    if result.get("connected"):
        return {
            "status": "success",
            "message": "MongoDB connection is working",
            "database": result.get("database")
        }
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "message": "MongoDB connection unavailable",
            "detail": result.get("error")
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
