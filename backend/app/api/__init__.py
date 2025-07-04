from fastapi import APIRouter

from .v1.auth import router as auth_router
from .v1.blogs import router as blogs_router
from .v1.blog_categories import router as blog_categories_router
from .v1.blog_tags import router as blog_tags_router
from .v1.courses import router as courses_router
from .v1.modules import router as modules_router
from .v1.lessons import router as lessons_router
from .v1.files import router as files_router
from .v1.users import router as users_router
from .v1.enrollments import router as enrollments_router

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# User management routes
api_router.include_router(users_router, prefix="/users", tags=["users"])

# Blog management routes
api_router.include_router(blogs_router, prefix="/blogs", tags=["blogs"])
api_router.include_router(blog_categories_router, prefix="/blog-categories", tags=["blog-categories"])
api_router.include_router(blog_tags_router, prefix="/blog-tags", tags=["blog-tags"])

# Learning management routes
api_router.include_router(courses_router, prefix="/courses", tags=["courses"])
api_router.include_router(modules_router, prefix="/modules", tags=["modules"])
api_router.include_router(lessons_router, prefix="/lessons", tags=["lessons"])

# File management routes
api_router.include_router(files_router, prefix="/files", tags=["files"])

# Enrollment management routes
api_router.include_router(enrollments_router, prefix="/enrollments", tags=["enrollments"])