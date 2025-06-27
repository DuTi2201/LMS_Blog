from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from ...core.database import get_db
from ..deps import get_current_user, get_optional_current_user, get_active_user, get_instructor_user, get_blog_service
from ...models.user import User, UserRole
from ...schemas.blog import (
    BlogPostCreate, BlogPostUpdate, BlogPostResponse, BlogPostListResponse,
    BlogCategoryCreate, BlogCategoryResponse, BlogTagCreate, BlogTagResponse,
    BlogSearchParams
)
from ...services.blog_service import BlogService

router = APIRouter()


@router.options("/")
@router.options("/{post_id}")
def options_handler():
    """Handle CORS preflight requests"""
    return {"message": "OK"}


@router.get("/", response_model=List[BlogPostResponse])
def get_blog_posts(
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    tag_id: Optional[UUID] = Query(None, description="Filter by tag ID"),
    author_id: Optional[UUID] = Query(None, description="Filter by author ID"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get list of blog posts with filtering and search"""
    # Logic phân quyền:
    # - Người dùng không đăng nhập: chỉ xem được bài published
    # - Người dùng đăng nhập: xem được bài của mình (cả published/unpublished) + bài published của người khác
    # - Admin/Instructor: xem được tất cả bài
    
    if not current_user:
        # Người dùng khách: chỉ xem bài published
        is_published = True
    elif current_user.role in [UserRole.ADMIN, UserRole.INSTRUCTOR]:
        # Admin/Instructor: có thể xem tất cả bài theo filter
        pass
    else:
        # Người dùng thường: nếu không filter theo author_id cụ thể
        if not author_id:
            # Lấy tất cả bài published + bài của user hiện tại
            posts = blog_service.get_posts_for_user(
                user_id=current_user.id,
                search_params=BlogSearchParams(
                    q=search,
                    category_id=category_id,
                    tag_ids=[tag_id] if tag_id else None,
                    is_published=is_published
                ),
                skip=skip,
                limit=limit
            )
            return posts
        elif author_id == current_user.id:
            # Xem bài của chính mình: có thể xem cả published/unpublished
            pass
        else:
            # Xem bài của người khác: chỉ xem published
            is_published = True
    
    search_params = BlogSearchParams(
        q=search,
        category_id=category_id,
        tag_ids=[tag_id] if tag_id else None,
        author_id=author_id,
        is_published=is_published
    )
    
    posts, total = blog_service.search_blog_posts(
        search_params=search_params,
        skip=skip,
        limit=limit
    )
    
    return posts


@router.get("/popular", response_model=List[BlogPostResponse])
def get_popular_posts(
    limit: int = Query(10, ge=1, le=50, description="Number of popular posts to return"),
    days: int = Query(30, ge=1, le=365, description="Time period in days"),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get popular blog posts"""
    posts = blog_service.get_popular_posts(limit=limit, days=days)
    return posts


@router.get("/recent", response_model=List[BlogPostResponse])
def get_recent_posts(
    limit: int = Query(10, ge=1, le=50, description="Number of recent posts to return"),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get recent blog posts"""
    posts = blog_service.get_recent_posts(limit=limit)
    return posts


@router.get("/my-posts", response_model=List[BlogPostResponse])
def get_my_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    current_user: User = Depends(get_active_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get current user's blog posts"""
    posts = blog_service.get_posts_by_author(
        author_id=current_user.id,
        skip=skip,
        limit=limit,
        is_published=is_published
    )
    return posts


@router.get("/{post_id}", response_model=BlogPostResponse)
def get_blog_post(
    post_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog post by ID"""
    post = blog_service.get_blog_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    # Check if user can view unpublished posts
    if not post.is_published:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Only author, admin, or instructor can view unpublished posts
        if (current_user.id != post.author_id and 
            current_user.role not in [UserRole.ADMIN, UserRole.INSTRUCTOR]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
    
    # Increment view count (you might want to implement rate limiting here)
    blog_service.increment_view_count(post_id)
    
    return post


@router.get("/slug/{slug}", response_model=BlogPostResponse)
def get_blog_post_by_slug(
    slug: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog post by slug"""
    post = blog_service.get_blog_post_by_slug(slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    # Check if user can view unpublished posts
    if not post.is_published:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Only author, admin, or instructor can view unpublished posts
        if (current_user.id != post.author_id and 
            current_user.role not in [UserRole.ADMIN, UserRole.INSTRUCTOR]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
    
    # Increment view count
    blog_service.increment_view_count(post.id)
    
    return post


@router.post("/", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
def create_blog_post(
    post_create: BlogPostCreate,
    current_user: User = Depends(get_instructor_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Create new blog post (Instructor+ only)"""
    try:
        post = blog_service.create_blog_post(post_create, author_id=current_user.id)
        return post
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{post_id}", response_model=BlogPostResponse)
def update_blog_post(
    post_id: UUID,
    post_update: BlogPostUpdate,
    current_user: User = Depends(get_active_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Update blog post"""
    # Get the existing post
    existing_post = blog_service.get_blog_post_by_id(post_id)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    # Check permissions: only author or admin can update
    if (current_user.id != existing_post.author_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this post"
        )
    
    try:
        post = blog_service.update_post(post_id, post_update, current_user.id)
        return post
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{post_id}")
def delete_blog_post(
    post_id: UUID,
    current_user: User = Depends(get_active_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Delete blog post"""
    # Get the existing post
    existing_post = blog_service.get_blog_post_by_id(post_id)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    # Check permissions: only author or admin can delete
    if (current_user.id != existing_post.author_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this post"
        )
    
    success = blog_service.delete_post(post_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete blog post"
        )
    
    return {"message": "Blog post deleted successfully"}


@router.post("/{post_id}/publish")
def publish_blog_post(
    post_id: UUID,
    current_user: User = Depends(get_active_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Publish blog post"""
    # Get the existing post
    existing_post = blog_service.get_blog_post_by_id(post_id)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    # Check permissions: only author or admin can publish
    if (current_user.id != existing_post.author_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to publish this post"
        )
    
    if existing_post.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post is already published"
        )
    
    # Publish the post
    post_update = BlogPostUpdate(is_published=True)
    post = blog_service.update_blog_post(post_id, post_update)
    
    return {"message": "Blog post published successfully"}


@router.post("/{post_id}/unpublish")
def unpublish_blog_post(
    post_id: UUID,
    current_user: User = Depends(get_active_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Unpublish blog post"""
    # Get the existing post
    existing_post = blog_service.get_blog_post_by_id(post_id)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    # Check permissions: only author or admin can unpublish
    if (current_user.id != existing_post.author_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to unpublish this post"
        )
    
    if not existing_post.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post is already unpublished"
        )
    
    # Unpublish the post
    post_update = BlogPostUpdate(is_published=False)
    post = blog_service.update_blog_post(post_id, post_update)
    
    return {"message": "Blog post unpublished successfully"}


@router.get("/{post_id}/stats")
def get_post_stats(
    post_id: UUID,
    current_user: User = Depends(get_active_user),
    blog_service: BlogService = Depends(get_blog_service)
):
    """Get blog post statistics"""
    post = blog_service.get_blog_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    # Check permissions: only author or admin can view stats
    if (current_user.id != post.author_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view post statistics"
        )
    
    stats = {
        "post_id": post_id,
        "title": post.title,
        "slug": post.slug,
        "view_count": post.view_count,
        "is_published": post.is_published,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "published_at": post.published_at,
        "category": post.category.name if post.category else None,
        "tags_count": len(post.tags) if hasattr(post, 'tags') else 0,
        "content_length": len(post.content) if post.content else 0
    }
    
    return stats