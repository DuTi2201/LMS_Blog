from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.blog import (
    BlogCategoryCreate, BlogCategoryUpdate, BlogCategoryResponse
)
from ...services.blog_service import BlogService
from ..deps import (
    get_current_user, get_admin_user, get_instructor_user,
    get_blog_service
)
from ...models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=List[BlogCategoryResponse])
def get_blog_categories(
    skip: int = Query(0, ge=0, description="Number of categories to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of categories to return"),
    search: Optional[str] = Query(None, description="Search categories by name"),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get list of blog categories"""
    categories = blog_service.get_blog_categories(
        skip=skip,
        limit=limit,
        search=search
    )
    return categories


@router.get("/{category_id}", response_model=BlogCategoryResponse)
def get_blog_category(
    category_id: int,
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog category by ID"""
    category = blog_service.get_blog_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog category not found"
        )
    return category


@router.get("/slug/{slug}", response_model=BlogCategoryResponse)
def get_blog_category_by_slug(
    slug: str,
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog category by slug"""
    category = blog_service.get_blog_category_by_slug(slug)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog category not found"
        )
    return category


@router.post("/", response_model=BlogCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_blog_category(
    category_create: BlogCategoryCreate,
    current_user: User = Depends(get_admin_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Create new blog category (Admin only)"""
    try:
        category = blog_service.create_blog_category(category_create)
        return category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{category_id}", response_model=BlogCategoryResponse)
def update_blog_category(
    category_id: int,
    category_update: BlogCategoryUpdate,
    current_user: User = Depends(get_admin_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Update blog category (Admin only)"""
    try:
        category = blog_service.update_blog_category(category_id, category_update)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog category not found"
            )
        return category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{category_id}")
def delete_blog_category(
    category_id: int,
    current_user: User = Depends(get_admin_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Delete blog category (Admin only)"""
    # Check if category has associated blog posts
    category = blog_service.get_blog_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog category not found"
        )
    
    # Check if category has blog posts
    if hasattr(category, 'blog_posts') and category.blog_posts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with associated blog posts. Please reassign or delete the posts first."
        )
    
    success = blog_service.delete_blog_category(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete blog category"
        )
    
    return {"message": "Blog category deleted successfully"}


@router.get("/{category_id}/posts")
def get_category_posts(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog posts in a specific category"""
    category = blog_service.get_blog_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog category not found"
        )
    
    posts = blog_service.get_posts_by_category(
        category_id=category_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "category": category,
        "posts": posts,
        "total": len(posts)
    }


@router.get("/{category_id}/stats")
def get_category_stats(
    category_id: int,
    current_user: User = Depends(get_current_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog category statistics"""
    category = blog_service.get_blog_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog category not found"
        )
    
    # Get category statistics
    stats = {
        "category_id": category_id,
        "name": category.name,
        "slug": category.slug,
        "total_posts": len(category.blog_posts) if hasattr(category, 'blog_posts') else 0,
        "published_posts": len([post for post in category.blog_posts if post.is_published]) if hasattr(category, 'blog_posts') else 0,
        "created_at": category.created_at,
        "updated_at": category.updated_at
    }
    
    return stats