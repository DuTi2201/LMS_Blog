from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc, asc, func
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional, Tuple
import re

from ..models.blog import BlogPost, BlogCategory, BlogTag, blog_post_tags
from ..models.user import User
from ..schemas.blog import (
    BlogPostCreate, BlogPostUpdate, BlogSearchParams,
    BlogCategoryCreate, BlogCategoryUpdate,
    BlogTagCreate, BlogTagUpdate
)


class BlogService:
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while self.db.query(BlogPost).filter(BlogPost.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    # Blog Category Methods
    def create_category(self, category_create: BlogCategoryCreate) -> BlogCategory:
        """Create a new blog category"""
        # Check if category name already exists
        existing_category = self.db.query(BlogCategory).filter(
            BlogCategory.name == category_create.name
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )
        
        db_category = BlogCategory(
            name=category_create.name,
            description=category_create.description
        )
        
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        
        return db_category
    
    def get_categories(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[BlogCategory]:
        """Get all blog categories"""
        query = self.db.query(BlogCategory)
        
        if search:
            query = query.filter(BlogCategory.name.ilike(f"%{search}%"))
        
        return query.offset(skip).limit(limit).all()
    
    def get_category_by_id(self, category_id: int) -> Optional[BlogCategory]:
        """Get category by ID"""
        return self.db.query(BlogCategory).filter(BlogCategory.id == category_id).first()
    
    def update_category(self, category_id: int, category_update: BlogCategoryUpdate) -> BlogCategory:
        """Update blog category"""
        category = self.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Check name uniqueness if name is being updated
        if category_update.name and category_update.name != category.name:
            existing_category = self.db.query(BlogCategory).filter(
                BlogCategory.name == category_update.name
            ).first()
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name already exists"
                )
        
        update_data = category_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        category.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def delete_category(self, category_id: int) -> bool:
        """Delete blog category"""
        category = self.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Check if category is being used by any posts
        posts_count = self.db.query(BlogPost).filter(BlogPost.category_id == category_id).count()
        if posts_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category. It is used by {posts_count} blog posts"
            )
        
        self.db.delete(category)
        self.db.commit()
        
        return True
    
    # Blog Tag Methods
    def create_tag(self, tag_create: BlogTagCreate) -> BlogTag:
        """Create a new blog tag"""
        # Check if tag name already exists
        existing_tag = self.db.query(BlogTag).filter(
            BlogTag.name == tag_create.name
        ).first()
        
        if existing_tag:
            return existing_tag  # Return existing tag instead of creating duplicate
        
        db_tag = BlogTag(name=tag_create.name)
        
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        
        return db_tag
    
    def get_tags(self, skip: int = 0, limit: int = 100) -> List[BlogTag]:
        """Get all blog tags"""
        return self.db.query(BlogTag).offset(skip).limit(limit).all()
    
    def get_blog_tags(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[BlogTag]:
        """Get blog tags with optional search"""
        query = self.db.query(BlogTag)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(BlogTag.name.ilike(search_term))
        
        return query.offset(skip).limit(limit).all()
    
    def get_tag_by_id(self, tag_id: int) -> Optional[BlogTag]:
        """Get tag by ID"""
        return self.db.query(BlogTag).filter(BlogTag.id == tag_id).first()
    
    def get_tag_by_name(self, name: str) -> Optional[BlogTag]:
        """Get tag by name"""
        return self.db.query(BlogTag).filter(BlogTag.name == name).first()
    
    def update_tag(self, tag_id: int, tag_update: BlogTagUpdate) -> BlogTag:
        """Update blog tag"""
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        # Check name uniqueness if name is being updated
        if tag_update.name and tag_update.name != tag.name:
            existing_tag = self.db.query(BlogTag).filter(
                BlogTag.name == tag_update.name
            ).first()
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tag name already exists"
                )
        
        update_data = tag_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)
        
        tag.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(tag)
        
        return tag
    
    def delete_tag(self, tag_id: int) -> bool:
        """Delete blog tag"""
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        self.db.delete(tag)
        self.db.commit()
        
        return True
    
    # Blog Post Methods
    def create_post(self, post_create: BlogPostCreate, author_id: int) -> BlogPost:
        """Create a new blog post"""
        # Generate slug from title
        slug = self._generate_slug(post_create.title)
        
        # Create blog post
        db_post = BlogPost(
            title=post_create.title,
            content=post_create.content,
            excerpt=post_create.excerpt,
            featured_image=post_create.featured_image,
            slug=slug,
            is_published=post_create.is_published,
            category_id=post_create.category_id,
            author_id=author_id,
            published_at=datetime.utcnow() if post_create.is_published else None
        )
        
        self.db.add(db_post)
        self.db.flush()  # Flush to get the ID
        
        # Add tags if provided
        if post_create.tag_ids:
            for tag_id in post_create.tag_ids:
                tag = self.get_tag_by_id(tag_id)
                if tag:
                    db_post.tags.append(tag)
        
        self.db.commit()
        self.db.refresh(db_post)
        
        return db_post
    
    def search_blog_posts(self, search_params: BlogSearchParams, skip: int = 0, limit: int = 10) -> Tuple[List[BlogPost], int]:
        """Search blog posts with parameters"""
        return self.get_posts(search_params)
    
    def get_posts(self, search_params: BlogSearchParams) -> Tuple[List[BlogPost], int]:
        """Get blog posts with search and pagination"""
        query = self.db.query(BlogPost).options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.category),
            joinedload(BlogPost.tags)
        )
        
        # Apply filters
        if search_params.q:
            search_term = f"%{search_params.q}%"
            query = query.filter(
                or_(
                    BlogPost.title.ilike(search_term),
                    BlogPost.content.ilike(search_term),
                    BlogPost.excerpt.ilike(search_term)
                )
            )
        
        if search_params.category_id:
            query = query.filter(BlogPost.category_id == search_params.category_id)
        
        if search_params.author_id:
            query = query.filter(BlogPost.author_id == search_params.author_id)
        
        if search_params.is_published is not None:
            query = query.filter(BlogPost.is_published == search_params.is_published)
        
        if search_params.tag_ids:
            query = query.join(BlogPost.tags).filter(
                BlogTag.id.in_(search_params.tag_ids)
            )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if search_params.sort_order == "desc":
            order_func = desc
        else:
            order_func = asc
        
        if search_params.sort_by == "title":
            query = query.order_by(order_func(BlogPost.title))
        elif search_params.sort_by == "view_count":
            query = query.order_by(order_func(BlogPost.view_count))
        elif search_params.sort_by == "published_at":
            query = query.order_by(order_func(BlogPost.published_at))
        elif search_params.sort_by == "updated_at":
            query = query.order_by(order_func(BlogPost.updated_at))
        else:  # default to created_at
            query = query.order_by(order_func(BlogPost.created_at))
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.size
        posts = query.offset(offset).limit(search_params.size).all()
        
        return posts, total
    
    def get_post_by_id(self, post_id: int) -> Optional[BlogPost]:
        """Get blog post by ID"""
        return self.db.query(BlogPost).options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.category),
            joinedload(BlogPost.tags)
        ).filter(BlogPost.id == post_id).first()
    
    def get_post_by_slug(self, slug: str) -> Optional[BlogPost]:
        """Get blog post by slug"""
        return self.db.query(BlogPost).options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.category),
            joinedload(BlogPost.tags)
        ).filter(BlogPost.slug == slug).first()
    
    def update_post(self, post_id: int, post_update: BlogPostUpdate, user_id: int) -> BlogPost:
        """Update blog post"""
        post = self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Check if user is the author or admin
        if post.author_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post"
            )
        
        update_data = post_update.model_dump(exclude_unset=True)
        
        # Handle title update (regenerate slug if needed)
        if "title" in update_data and update_data["title"] != post.title:
            update_data["slug"] = self._generate_slug(update_data["title"])
        
        # Handle publication status
        if "is_published" in update_data:
            if update_data["is_published"] and not post.is_published:
                update_data["published_at"] = datetime.utcnow()
            elif not update_data["is_published"] and post.is_published:
                update_data["published_at"] = None
        
        # Handle tags
        if "tag_ids" in update_data:
            tag_ids = update_data.pop("tag_ids")
            # Clear existing tags
            post.tags.clear()
            # Add new tags
            if tag_ids:
                for tag_id in tag_ids:
                    tag = self.get_tag_by_id(tag_id)
                    if tag:
                        post.tags.append(tag)
        
        # Update other fields
        for field, value in update_data.items():
            setattr(post, field, value)
        
        post.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(post)
        
        return post
    
    def delete_post(self, post_id: int, user_id: int) -> bool:
        """Delete blog post"""
        post = self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Check if user is the author or admin
        if post.author_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post"
            )
        
        self.db.delete(post)
        self.db.commit()
        
        return True
    
    def increment_view_count(self, post_id: int) -> BlogPost:
        """Increment view count for a blog post"""
        post = self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        post.view_count += 1
        self.db.commit()
        self.db.refresh(post)
        
        return post
    
    def get_popular_posts(self, limit: int = 10) -> List[BlogPost]:
        """Get most popular blog posts by view count"""
        return self.db.query(BlogPost).options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.category),
            joinedload(BlogPost.tags)
        ).filter(
            BlogPost.is_published == True
        ).order_by(
            desc(BlogPost.view_count)
        ).limit(limit).all()
    
    def get_recent_posts(self, limit: int = 10) -> List[BlogPost]:
        """Get most recent published blog posts"""
        return self.db.query(BlogPost).options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.category),
            joinedload(BlogPost.tags)
        ).filter(
            BlogPost.is_published == True
        ).order_by(
            desc(BlogPost.published_at)
        ).limit(limit).all()
    
    def get_posts_by_author(self, author_id: int, skip: int = 0, limit: int = 10) -> List[BlogPost]:
        """Get blog posts by specific author"""
        return self.db.query(BlogPost).options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.category),
            joinedload(BlogPost.tags)
        ).filter(
            BlogPost.author_id == author_id
        ).order_by(
            desc(BlogPost.created_at)
        ).offset(skip).limit(limit).all()
    
    def get_posts_by_category(self, category_id: int, skip: int = 0, limit: int = 10) -> List[BlogPost]:
        """Get blog posts by category"""
        return self.db.query(BlogPost).options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.category),
            joinedload(BlogPost.tags)
        ).filter(
            and_(
                BlogPost.category_id == category_id,
                BlogPost.is_published == True
            )
        ).order_by(
            desc(BlogPost.published_at)
        ).offset(skip).limit(limit).all()
    
    def get_posts_by_tag(self, tag_id: int, skip: int = 0, limit: int = 10) -> List[BlogPost]:
        """Get blog posts by tag"""
        return self.db.query(BlogPost).options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.category),
            joinedload(BlogPost.tags)
        ).join(BlogPost.tags).filter(
            and_(
                BlogTag.id == tag_id,
                BlogPost.is_published == True
            )
        ).order_by(
            desc(BlogPost.published_at)
        ).offset(skip).limit(limit).all()