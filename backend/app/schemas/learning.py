from typing import Optional, List
from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from uuid import UUID
from .user import UserResponse
from typing import Optional, List


# Course Schemas
class CourseBase(BaseModel):
    title: str
    description: str
    featured_image: Optional[str] = None
    is_published: bool = False
    level: str = "beginner"  # beginner, intermediate, advanced
    duration_hours: Optional[int] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError("Title must be at least 5 characters long")
        return v.strip()
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Description must be at least 10 characters long")
        return v.strip()
    
    @field_validator("level")
    @classmethod
    def validate_level(cls, v):
        allowed_levels = ["beginner", "intermediate", "advanced"]
        if v not in allowed_levels:
            raise ValueError(f"Level must be one of: {', '.join(allowed_levels)}")
        return v


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: Optional[bool] = None
    level: Optional[str] = None
    duration_hours: Optional[int] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and len(v.strip()) < 5:
            raise ValueError("Title must be at least 5 characters long")
        return v.strip() if v else v
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError("Description must be at least 10 characters long")
        return v.strip() if v else v
    
    @field_validator("level")
    @classmethod
    def validate_level(cls, v):
        allowed_levels = ["beginner", "intermediate", "advanced"]
        if v is not None and v not in allowed_levels:
            raise ValueError(f"Level must be one of: {', '.join(allowed_levels)}")
        return v


class CourseResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    difficulty_level: str
    estimated_duration: Optional[int] = None
    is_published: bool
    price: float
    enrollment_count: int = 0
    created_at: datetime
    updated_at: datetime
    instructor_id: UUID
    modules: Optional[List['ModuleResponse']] = []
    
    model_config = ConfigDict(from_attributes=True)


# Module Schemas
class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int
    course_id: UUID
    is_published: bool = False
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return v.strip()
    
    @field_validator("order_index")
    @classmethod
    def validate_order_index(cls, v):
        if v < 0:
            raise ValueError("Order index must be a non-negative integer")
        return v


class ModuleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int
    is_published: bool = False
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return v.strip()
    
    @field_validator("order_index")
    @classmethod
    def validate_order_index(cls, v):
        if v < 0:
            raise ValueError("Order index must be a non-negative integer")
        return v


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    is_published: Optional[bool] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return v.strip() if v else v
    
    @field_validator("order_index")
    @classmethod
    def validate_order_index(cls, v):
        if v is not None and v < 0:
            raise ValueError("Order index must be a non-negative integer")
        return v


class LessonResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    lesson_date: Optional[datetime] = None
    instructor_name: Optional[str] = None
    zoom_link: Optional[str] = None
    quiz_link: Optional[str] = None
    notification: Optional[str] = None
    order_index: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    module_id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class ModuleResponse(ModuleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Related objects
    lessons: Optional[List[LessonResponse]] = None
    
    model_config = ConfigDict(from_attributes=True)


# Lesson Schemas
class LessonBase(BaseModel):
    title: str
    content: str
    order: int
    module_id: str
    lesson_type: str = "text"  # text, video, quiz
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return v.strip()
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Content must be at least 10 characters long")
        return v.strip()
    
    @field_validator("order")
    @classmethod
    def validate_order(cls, v):
        if v < 0:
            raise ValueError("Order must be a non-negative integer")
        return v
    
    @field_validator("lesson_type")
    @classmethod
    def validate_lesson_type(cls, v):
        allowed_types = ["text", "video", "quiz"]
        if v not in allowed_types:
            raise ValueError(f"Lesson type must be one of: {', '.join(allowed_types)}")
        return v


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    lesson_type: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return v.strip() if v else v
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError("Content must be at least 10 characters long")
        return v.strip() if v else v
    
    @field_validator("order")
    @classmethod
    def validate_order(cls, v):
        if v is not None and v < 0:
            raise ValueError("Order must be a non-negative integer")
        return v
    
    @field_validator("lesson_type")
    @classmethod
    def validate_lesson_type(cls, v):
        allowed_types = ["text", "video", "quiz"]
        if v is not None and v not in allowed_types:
            raise ValueError(f"Lesson type must be one of: {', '.join(allowed_types)}")
        return v


class LessonResponse(LessonBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    # Related objects
    attachments: Optional[List[dict]] = None  # Will be populated with attachment data
    
    class Config:
        from_attributes = True


# Lesson Attachment Schemas
class LessonAttachmentBase(BaseModel):
    title: str
    file_url: str
    file_type: str
    file_size: int
    lesson_id: str
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return v.strip()


class LessonAttachmentCreate(LessonAttachmentBase):
    pass


class LessonAttachmentUpdate(BaseModel):
    title: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return v.strip() if v else v


class LessonAttachmentResponse(LessonAttachmentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# User Enrollment Schemas
class UserEnrollmentBase(BaseModel):
    user_id: UUID
    course_id: UUID
    is_completed: bool = False
    progress_percentage: float = 0.0
    
    @field_validator("progress_percentage")
    @classmethod
    def validate_progress_percentage(cls, v):
        if v < 0.0 or v > 100.0:
            raise ValueError("Progress percentage must be between 0 and 100")
        return v


class UserEnrollmentCreate(UserEnrollmentBase):
    pass


class UserEnrollmentUpdate(BaseModel):
    is_completed: Optional[bool] = None
    progress_percentage: Optional[float] = None
    
    @field_validator("progress_percentage")
    @classmethod
    def validate_progress_percentage(cls, v):
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError("Progress percentage must be between 0 and 100")
        return v


class UserEnrollmentResponse(UserEnrollmentBase):
    id: UUID
    enrolled_at: datetime
    last_accessed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Related objects
    user: Optional[UserResponse] = None  # Will be populated with user data
    course: Optional[CourseResponse] = None  # Will be populated with course data
    
    class Config:
        from_attributes = True


# Course List Response (for pagination)
class CourseListResponse(BaseModel):
    items: List[CourseResponse]
    total: int
    page: int
    size: int
    pages: int


# Course Search Schema
class CourseSearchParams(BaseModel):
    q: Optional[str] = None  # Search query
    instructor_id: Optional[int] = None
    difficulty_level: Optional[str] = None
    is_published: Optional[bool] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
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
        allowed_fields = ["created_at", "updated_at", "title", "price"]
        if v not in allowed_fields:
            raise ValueError(f"Sort by must be one of: {', '.join(allowed_fields)}")
        return v
    
    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        return v
    
    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty_level(cls, v):
        allowed_levels = ["beginner", "intermediate", "advanced"]
        if v is not None and v not in allowed_levels:
            raise ValueError(f"Difficulty level must be one of: {', '.join(allowed_levels)}")
        return v