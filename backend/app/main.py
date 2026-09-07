import os
import sys

# Ensure project root is accessible for ml/ module imports
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_THIS_DIR))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.config import settings
from app.core.database import Base, engine
from app.api import api_router
from app.core.logging_config import logger

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="SIH26100: AI-Powered Integrated Bid Compliance Verification Platform for GeM Procurement.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json"
)

# Structured Database Error Handlers
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Database Integrity Error on {request.url.path}: {str(exc.orig)}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_INTEGRITY_ERROR",
                "message": "Database constraint violation. Ensure unique identifiers and foreign keys are valid.",
                "detail": str(exc.orig) if settings.ENV == "development" else "Unique or foreign key constraint violation"
            }
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database Error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "A database operation error occurred while processing the request."
            }
        }
    )

# CORS Middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list if settings.cors_origins_list else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Mount API Router (both with /api prefix and root for full flexibility)
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "SIH26100 Compliance Platform",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs"
    }

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "SIH26100 Compliance Platform"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
