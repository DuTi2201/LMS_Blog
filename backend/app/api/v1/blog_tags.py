from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.blog import (
    BlogTagCreate, BlogTagUpdate, BlogTagResponse
)
from ...services.blog_service import BlogService
from ..deps import (
    get_current_user, get_admin_user, get_instructor_user,
    get_blog_service
)
from ...models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=List[BlogTagResponse])
def get_blog_tags(
    skip: int = Query(0, ge=0, description="Number of tags to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of tags to return"),
    search: Optional[str] = Query(None, description="Search tags by name"),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get list of blog tags"""
    tags = blog_service.get_blog_tags(
        skip=skip,
        limit=limit,
        search=search
    )
    return tags


@router.get("/popular")
def get_popular_tags(
    limit: int = Query(20, ge=1, le=100, description="Number of popular tags to return"),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get popular blog tags (ordered by usage count)"""
    tags = blog_service.get_popular_tags(limit=limit)
    return tags


@router.get("/{tag_id}", response_model=BlogTagResponse)
def get_blog_tag(
    tag_id: int,
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog tag by ID"""
    tag = blog_service.get_blog_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog tag not found"
        )
    return tag


@router.get("/slug/{slug}", response_model=BlogTagResponse)
def get_blog_tag_by_slug(
    slug: str,
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog tag by slug"""
    tag = blog_service.get_blog_tag_by_slug(slug)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog tag not found"
        )
    return tag


@router.post("/", response_model=BlogTagResponse, status_code=status.HTTP_201_CREATED)
def create_blog_tag(
    tag_create: BlogTagCreate,
    current_user: User = Depends(get_instructor_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Create new blog tag (Instructor+ only)"""
    try:
        tag = blog_service.create_blog_tag(tag_create)
        return tag
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{tag_id}", response_model=BlogTagResponse)
def update_blog_tag(
    tag_id: int,
    tag_update: BlogTagUpdate,
    current_user: User = Depends(get_admin_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Update blog tag (Admin only)"""
    try:
        tag = blog_service.update_blog_tag(tag_id, tag_update)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog tag not found"
            )
        return tag
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{tag_id}")
def delete_blog_tag(
    tag_id: int,
    current_user: User = Depends(get_admin_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Delete blog tag (Admin only)"""
    # Check if tag has associated blog posts
    tag = blog_service.get_blog_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog tag not found"
        )
    
    # Check if tag has blog posts
    if hasattr(tag, 'blog_posts') and tag.blog_posts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete tag with associated blog posts. Please remove the tag from posts first."
        )
    
    success = blog_service.delete_blog_tag(tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete blog tag"
        )
    
    return {"message": "Blog tag deleted successfully"}


@router.get("/{tag_id}/posts")
def get_tag_posts(
    tag_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog posts with a specific tag"""
    tag = blog_service.get_blog_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog tag not found"
        )
    
    posts = blog_service.get_posts_by_tag(
        tag_id=tag_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "tag": tag,
        "posts": posts,
        "total": len(posts)
    }


@router.get("/{tag_id}/stats")
def get_tag_stats(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog tag statistics"""
    tag = blog_service.get_blog_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog tag not found"
        )
    
    # Get tag statistics
    stats = {
        "tag_id": tag_id,
        "name": tag.name,
        "slug": tag.slug,
        "color": tag.color,
        "total_posts": len(tag.blog_posts) if hasattr(tag, 'blog_posts') else 0,
        "published_posts": len([post for post in tag.blog_posts if post.is_published]) if hasattr(tag, 'blog_posts') else 0,
        "created_at": tag.created_at,
        "updated_at": tag.updated_at
    }
    
    return stats


@router.post("/bulk-create", response_model=List[BlogTagResponse])
def bulk_create_tags(
    tag_names: List[str],
    current_user: User = Depends(get_instructor_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Bulk create blog tags (Instructor+ only)"""
    if len(tag_names) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create more than 50 tags at once"
        )
    
    created_tags = []
    errors = []
    
    for tag_name in tag_names:
        try:
            tag_create = BlogTagCreate(name=tag_name.strip())
            tag = blog_service.create_blog_tag(tag_create)
            created_tags.append(tag)
        except ValueError as e:
            errors.append({"tag_name": tag_name, "error": str(e)})
    
    result = {
        "created_tags": created_tags,
        "created_count": len(created_tags),
        "errors": errors,
        "error_count": len(errors)
    }
    
    return result