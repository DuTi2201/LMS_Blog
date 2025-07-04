from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
import os
import traceback
from contextlib import asynccontextmanager

from .core.config import settings
from .core.database import init_db, check_db_connection, engine, Base
from .api import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up LMS Backend API...")
    
    # Check database connection
    if not check_db_connection():
        logger.error("Failed to connect to database")
        raise Exception("Database connection failed")
    
    logger.info("Database connection successful")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    # Create upload directories
    upload_dirs = [
        settings.UPLOAD_DIR,
        os.path.join(settings.UPLOAD_DIR, "images"),
        os.path.join(settings.UPLOAD_DIR, "videos"),
        os.path.join(settings.UPLOAD_DIR, "documents"),
        os.path.join(settings.UPLOAD_DIR, "attachments"),
        os.path.join(settings.UPLOAD_DIR, "temp")
    ]
    
    for directory in upload_dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created upload directory: {directory}")
    
    logger.info("LMS Backend API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down LMS Backend API...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Learning Management System Backend API",
    version=settings.VERSION,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Add CORS middleware first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://192.168.2.101:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost", "192.168.2.101"]
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} - "
        f"Time: {process_time:.4f}s - "
        f"Path: {request.url.path}"
    )
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    logger.warning(
        f"HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(
        f"HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(
        f"Validation error on {request.method} {request.url.path}: {exc.errors()}"
    )
    
    # Ensure validation errors are JSON serializable
    try:
        error_details = exc.errors()
        # Convert any non-serializable objects to strings
        serializable_details = []
        for error in error_details:
            serializable_error = {}
            for key, value in error.items():
                try:
                    # Test if value is JSON serializable
                    import json
                    json.dumps(value)
                    serializable_error[key] = value
                except (TypeError, ValueError):
                    serializable_error[key] = str(value)
            serializable_details.append(serializable_error)
    except Exception:
        serializable_details = [{"message": "Validation error occurred but details could not be serialized"}]
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation error",
            "details": serializable_details,
            "status_code": 422,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    # Log detailed error information
    error_traceback = traceback.format_exc()
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}:\n"
        f"Exception: {type(exc).__name__}: {str(exc)}\n"
        f"Traceback:\n{error_traceback}"
    )
    
    # Also log request body if available
    try:
        if hasattr(request, '_body'):
            body = await request.body()
            if body:
                logger.error(f"Request body: {body.decode('utf-8')[:1000]}")
    except Exception as e:
        logger.error(f"Could not log request body: {e}")
    
    # Ensure all values are JSON serializable
    try:
        detail_str = str(exc)
    except Exception:
        detail_str = f"{type(exc).__name__}: <unable to convert to string>"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path),
            "detail": detail_str,
            "traceback": error_traceback if settings.DEBUG else None
        }
    )





@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to LMS Backend API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
        "redoc": f"{settings.API_V1_STR}/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = check_db_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "version": settings.VERSION
    }


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )