from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from app.models.blog import BlogPost, BlogCategory, BlogTag, blog_post_tags
from app.models.user import User, UserRole
from app.schemas.blog import (
    BlogPostCreate, BlogPostUpdate, BlogCategoryCreate, BlogCategoryUpdate,
    BlogTagCreate, BlogTagUpdate, BlogSearchParams
)
from app.core.utils import generate_slug, calculate_read_time


class BlogService:
    def __init__(self, db: Session):
        self.db = db
    
    # Blog Post Methods
    def create_post(self, post_create: BlogPostCreate, author_id: UUID) -> BlogPost:
        """Create a new blog post"""
        # Generate slug from title
        slug = generate_slug(post_create.title)
        
        # Ensure slug is unique
        counter = 1
        original_slug = slug
        while self.get_post_by_slug(slug):
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Calculate word count and read time
        word_count = len(post_create.content.split())
        read_time = calculate_read_time(word_count)
        
        # Create post data
        post_data = {
            "title": post_create.title,
            "slug": slug,
            "content": post_create.content,
            "excerpt": post_create.excerpt,
            "featured_image_url": post_create.featured_image,
            "author_id": author_id,
            "category_id": post_create.category_id,
            "word_count": word_count,
            "read_time_minutes": read_time,
            "status": "published" if post_create.is_published else "draft"
        }
        
        # Set published_at if publishing
        if post_create.is_published:
            post_data["published_at"] = datetime.utcnow()
        
        post = BlogPost(**post_data)
        self.db.add(post)
        self.db.flush()  # Get the ID without committing
        
        # Add tags if provided
        if post_create.tag_ids:
            for tag_id in post_create.tag_ids:
                tag = self.get_tag_by_id(tag_id)
                if tag:
                    post.tags.append(tag)
        
        self.db.commit()
        self.db.refresh(post)
        
        return post
    
    def get_posts(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        status: Optional[str] = None,
        category_id: Optional[UUID] = None,
        author_id: Optional[UUID] = None,
        search: Optional[str] = None,
        tag_ids: Optional[List[UUID]] = None
    ) -> Dict[str, Any]:
        """Get blog posts with filtering and pagination"""
        query = self.db.query(BlogPost)
        
        # Apply filters
        if status:
            query = query.filter(BlogPost.status == status)
        
        if category_id:
            query = query.filter(BlogPost.category_id == category_id)
        
        if author_id:
            query = query.filter(BlogPost.author_id == author_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    BlogPost.title.ilike(search_term),
                    BlogPost.content.ilike(search_term),
                    BlogPost.excerpt.ilike(search_term)
                )
            )
        
        if tag_ids:
            query = query.join(BlogPost.tags).filter(BlogTag.id.in_(tag_ids))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        posts = query.order_by(desc(BlogPost.created_at)).offset(skip).limit(limit).all()
        
        return {
            "posts": posts,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def get_published_posts(
        self, 
        skip: int = 0, 
        limit: int = 10,
        category_id: Optional[UUID] = None,
        search: Optional[str] = None,
        tag_ids: Optional[List[UUID]] = None
    ) -> Dict[str, Any]:
        """Get published blog posts for public viewing"""
        return self.get_posts(
            skip=skip,
            limit=limit,
            status="published",
            category_id=category_id,
            search=search,
            tag_ids=tag_ids
        )
    
    def get_post_by_id(self, post_id: UUID) -> Optional[BlogPost]:
        """Get blog post by ID"""
        return self.db.query(BlogPost).filter(BlogPost.id == post_id).first()
    
    def get_post_by_slug(self, slug: str) -> Optional[BlogPost]:
        """Get blog post by slug"""
        return self.db.query(BlogPost).filter(BlogPost.slug == slug).first()
    
    def get_published_post_by_slug(self, slug: str) -> Optional[BlogPost]:
        """Get published blog post by slug"""
        return self.db.query(BlogPost).filter(
            and_(BlogPost.slug == slug, BlogPost.status == "published")
        ).first()
    
    def increment_view_count(self, post_id: UUID) -> bool:
        """Increment view count for a blog post"""
        post = self.get_post_by_id(post_id)
        if post:
            post.view_count += 1
            self.db.commit()
            return True
        return False
    
    def search_posts(self, search_params: BlogSearchParams) -> Dict[str, Any]:
        """Advanced search for blog posts"""
        query = self.db.query(BlogPost)
        
        # Text search
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    BlogPost.title.ilike(search_term),
                    BlogPost.content.ilike(search_term),
                    BlogPost.excerpt.ilike(search_term)
                )
            )
        
        # Category filter
        if search_params.category_id:
            query = query.filter(BlogPost.category_id == search_params.category_id)
        
        # Author filter
        if search_params.author_id:
            query = query.filter(BlogPost.author_id == search_params.author_id)
        
        # Status filter
        if search_params.status:
            query = query.filter(BlogPost.status == search_params.status)
        
        # Tag filters
        if search_params.tag_ids:
            query = query.join(BlogPost.tags).filter(BlogTag.id.in_(search_params.tag_ids))
        
        # Date range filters
        if search_params.date_from:
            query = query.filter(BlogPost.created_at >= search_params.date_from)
        
        if search_params.date_to:
            query = query.filter(BlogPost.created_at <= search_params.date_to)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if search_params.sort_by == "title":
            if search_params.sort_order == "desc":
                query = query.order_by(desc(BlogPost.title))
            else:
                query = query.order_by(BlogPost.title)
        elif search_params.sort_by == "created_at":
            if search_params.sort_order == "desc":
                query = query.order_by(desc(BlogPost.created_at))
            else:
                query = query.order_by(BlogPost.created_at)
        elif search_params.sort_by == "view_count":
            if search_params.sort_order == "desc":
                query = query.order_by(desc(BlogPost.view_count))
            else:
                query = query.order_by(BlogPost.view_count)
        else:
            # Default sorting
            query = query.order_by(desc(BlogPost.created_at))
        
        # Apply pagination
        posts = query.offset(search_params.skip).limit(search_params.limit).all()
        
        return {
            "posts": posts,
            "total": total,
            "skip": search_params.skip,
            "limit": search_params.limit
        }
    
    def update_post(self, post_id: UUID, post_update: BlogPostUpdate, user_id: UUID) -> BlogPost:
        """Update blog post"""
        post = self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Check if user can update this post
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only author or admin/instructor can update
        if post.author_id != user_id and user.role not in [UserRole.ADMIN, UserRole.INSTRUCTOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post"
            )
        
        # Prepare update data
        update_data = post_update.model_dump(exclude_unset=True)
        
        # Handle slug update if title changed
        if "title" in update_data:
            new_slug = generate_slug(update_data["title"])
            # Ensure slug is unique (excluding current post)
            counter = 1
            original_slug = new_slug
            while True:
                existing_post = self.get_post_by_slug(new_slug)
                if not existing_post or existing_post.id == post_id:
                    break
                new_slug = f"{original_slug}-{counter}"
                counter += 1
            update_data["slug"] = new_slug
        
        # Handle content update (recalculate word count and read time)
        if "content" in update_data:
            word_count = len(update_data["content"].split())
            update_data["word_count"] = word_count
            update_data["read_time_minutes"] = calculate_read_time(word_count)
        
        # Handle featured image
        if "featured_image" in update_data:
            update_data["featured_image_url"] = update_data.pop("featured_image")
        
        # Handle tags update
        if "tag_ids" in update_data:
            tag_ids = update_data.pop("tag_ids")
            if tag_ids is not None:
                # Clear existing tags
                post.tags.clear()
                # Add new tags
                for tag_id in tag_ids:
                    tag = self.get_tag_by_id(tag_id)
                    if tag:
                        post.tags.append(tag)
        
        # Handle is_published separately by updating status
        if 'is_published' in update_data:
            is_published = update_data.pop('is_published')
            if is_published:
                post.status = "published"
                if not post.published_at:
                    post.published_at = datetime.utcnow()
            else:
                post.status = "draft"
                post.published_at = None
        
        # Update other fields
        for field, value in update_data.items():
            setattr(post, field, value)
        
        post.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(post)
        
        return post
    
    def delete_post(self, post_id: UUID, user_id: UUID) -> bool:
        """Delete blog post"""
        post = self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Check if user can delete this post
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only author or admin can delete
        if post.author_id != user_id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post"
            )
        
        self.db.delete(post)
        self.db.commit()
        
        return True
    
    # Blog Category Methods
    def create_category(self, category_create: BlogCategoryCreate) -> BlogCategory:
        """Create a new blog category"""
        # Generate slug from name
        slug = generate_slug(category_create.name)
        
        # Ensure slug is unique
        counter = 1
        original_slug = slug
        while self.get_category_by_slug(slug):
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        category = BlogCategory(
            name=category_create.name,
            slug=slug,
            description=category_create.description
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def get_categories(self, skip: int = 0, limit: int = 100) -> List[BlogCategory]:
        """Get all blog categories"""
        return self.db.query(BlogCategory).offset(skip).limit(limit).all()
    
    def get_category_by_id(self, category_id: UUID) -> Optional[BlogCategory]:
        """Get blog category by ID"""
        return self.db.query(BlogCategory).filter(BlogCategory.id == category_id).first()
    
    def get_category_by_slug(self, slug: str) -> Optional[BlogCategory]:
        """Get blog category by slug"""
        return self.db.query(BlogCategory).filter(BlogCategory.slug == slug).first()
    
    def update_category(self, category_id: UUID, category_update: BlogCategoryUpdate) -> BlogCategory:
        """Update blog category"""
        category = self.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog category not found"
            )
        
        update_data = category_update.model_dump(exclude_unset=True)
        
        # Handle slug update if name changed
        if "name" in update_data:
            new_slug = generate_slug(update_data["name"])
            # Ensure slug is unique (excluding current category)
            counter = 1
            original_slug = new_slug
            while True:
                existing_category = self.get_category_by_slug(new_slug)
                if not existing_category or existing_category.id == category_id:
                    break
                new_slug = f"{original_slug}-{counter}"
                counter += 1
            update_data["slug"] = new_slug
        
        for field, value in update_data.items():
            setattr(category, field, value)
        
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def delete_category(self, category_id: UUID) -> bool:
        """Delete blog category"""
        category = self.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog category not found"
            )
        
        # Check if category has posts
        posts_count = self.db.query(BlogPost).filter(BlogPost.category_id == category_id).count()
        if posts_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with existing posts"
            )
        
        self.db.delete(category)
        self.db.commit()
        
        return True
    
    # Blog Tag Methods
    def create_tag(self, tag_create: BlogTagCreate) -> BlogTag:
        """Create a new blog tag"""
        # Check if tag already exists
        existing_tag = self.db.query(BlogTag).filter(BlogTag.name == tag_create.name.lower()).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag already exists"
            )
        
        tag = BlogTag(name=tag_create.name.lower())
        
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        
        return tag
    
    def get_tags(self, skip: int = 0, limit: int = 100) -> List[BlogTag]:
        """Get all blog tags"""
        return self.db.query(BlogTag).offset(skip).limit(limit).all()
    
    def get_tag_by_id(self, tag_id: UUID) -> Optional[BlogTag]:
        """Get blog tag by ID"""
        return self.db.query(BlogTag).filter(BlogTag.id == tag_id).first()
    
    def get_tag_by_name(self, name: str) -> Optional[BlogTag]:
        """Get blog tag by name"""
        return self.db.query(BlogTag).filter(BlogTag.name == name.lower()).first()
    
    def update_tag(self, tag_id: UUID, tag_update: BlogTagUpdate) -> BlogTag:
        """Update blog tag"""
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog tag not found"
            )
        
        update_data = tag_update.model_dump(exclude_unset=True)
        
        # Check if new name already exists (excluding current tag)
        if "name" in update_data:
            existing_tag = self.get_tag_by_name(update_data["name"])
            if existing_tag and existing_tag.id != tag_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tag name already exists"
                )
        
        for field, value in update_data.items():
            setattr(tag, field, value)
        
        self.db.commit()
        self.db.refresh(tag)
        
        return tag
    
    def delete_tag(self, tag_id: UUID) -> bool:
        """Delete blog tag"""
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog tag not found"
            )
        
        self.db.delete(tag)
        self.db.commit()
        
        return True
    
    def get_popular_tags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular tags based on usage count"""
        result = (
            self.db.query(
                BlogTag.id,
                BlogTag.name,
                func.count(blog_post_tags.c.post_id).label("usage_count")
            )
            .join(blog_post_tags, BlogTag.id == blog_post_tags.c.tag_id)
            .group_by(BlogTag.id, BlogTag.name)
            .order_by(desc(func.count(blog_post_tags.c.post_id)))
            .limit(limit)
            .all()
        )
        
        return [
            {
                "id": row.id,
                "name": row.name,
                "usage_count": row.usage_count
            }
            for row in result
        ]
