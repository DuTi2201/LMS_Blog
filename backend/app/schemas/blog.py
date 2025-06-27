from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from .user import UserResponse


# Blog Category Schemas
class BlogCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Category name must be at least 2 characters long")
        return v.strip()


class BlogCategoryCreate(BlogCategoryBase):
    pass


class BlogCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError("Category name must be at least 2 characters long")
        return v.strip() if v else v


class BlogCategoryResponse(BlogCategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Blog Tag Schemas
class BlogTagBase(BaseModel):
    name: str
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Tag name must be at least 2 characters long")
        return v.strip().lower()


class BlogTagCreate(BlogTagBase):
    pass


class BlogTagUpdate(BaseModel):
    name: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError("Tag name must be at least 2 characters long")
        return v.strip().lower() if v else v


class BlogTagResponse(BlogTagBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Blog Post Schemas
class BlogPostBase(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: bool = False
    category_id: Optional[UUID] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError("Title must be at least 5 characters long")
        return v.strip()
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Content must be at least 10 characters long")
        return v.strip()


class BlogPostCreate(BlogPostBase):
    tag_ids: Optional[List[UUID]] = []


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: Optional[bool] = None
    category_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and len(v.strip()) < 5:
            raise ValueError("Title must be at least 5 characters long")
        return v.strip() if v else v
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError("Content must be at least 10 characters long")
        return v.strip() if v else v


class BlogPostResponse(BlogPostBase):
    id: UUID
    slug: str
    author_id: UUID
    view_count: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    # Related objects
    author: Optional[UserResponse] = None  # Will be populated with user data
    category: Optional[BlogCategoryResponse] = None
    tags: List[BlogTagResponse] = []
    
    class Config:
        from_attributes = True


# Blog Post List Response (for pagination)
class BlogPostListResponse(BaseModel):
    items: List[BlogPostResponse]
    total: int
    page: int
    size: int
    pages: int


# Blog Search Schema
class BlogSearchParams(BaseModel):
    q: Optional[str] = None  # Search query
    category_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None
    author_id: Optional[UUID] = None
    is_published: Optional[bool] = None
    page: int = 1
    size: int = 10
    sort_by: str = "created_at"
    sort_order: str = "desc"
    
    @field_validator("page")
    @classmethod
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be greater than 0")
        return v
    
    @field_validator("size")
    @classmethod
    def validate_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Size must be between 1 and 100")
        return v
    
    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        allowed_fields = ["created_at", "updated_at", "title", "view_count", "published_at"]
        if v not in allowed_fields:
            raise ValueError(f"Sort by must be one of: {', '.join(allowed_fields)}")
        return v
    
    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        return v