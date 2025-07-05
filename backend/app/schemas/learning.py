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
    created_at: datetime
    updated_at: datetime
    instructor_id: UUID
    
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


class LessonResponseOld(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    lesson_date: Optional[datetime] = None
    instructor: Optional[str] = None
    zoom_link: Optional[str] = None
    quiz_link: Optional[str] = None
    notification: Optional[str] = None
    order_index: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    module_id: UUID
    video_url: Optional[str] = None
    duration: Optional[int] = None
    attachments: Optional[List[dict]] = None
    
    model_config = ConfigDict(from_attributes=True)


class ModuleResponse(ModuleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Related objects - removed to prevent circular reference
    # lessons: Optional[List[LessonResponseOld]] = None
    
    model_config = ConfigDict(from_attributes=True)


# Lesson Schemas - Updated to match frontend
class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructor: Optional[str] = None
    zoom_link: Optional[str] = None  # Changed from zoomLink to zoom_link for database
    quiz_link: Optional[str] = None  # Changed from quizLink to quiz_link for database
    notification: Optional[str] = None
    duration: Optional[int] = None  # Duration in minutes
    video_url: Optional[str] = None
    order_index: int = 0
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Title must not be empty")
        return v.strip()
    
    @field_validator("order_index")
    @classmethod
    def validate_order_index(cls, v):
        if v < 0:
            raise ValueError("Order index must be a non-negative integer")
        return v


class LessonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    instructor: Optional[str] = None
    zoom_link: Optional[str] = None
    quiz_link: Optional[str] = None
    notification: Optional[str] = None
    duration: Optional[int] = None
    video_url: Optional[str] = None
    order_index: int = 0
    attachments: Optional[List[dict]] = None  # Added attachments field
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Title must not be empty")
        return v.strip()
    
    @field_validator("order_index")
    @classmethod
    def validate_order_index(cls, v):
        if v < 0:
            raise ValueError("Order index must be a non-negative integer")
        return v


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None
    zoom_link: Optional[str] = None
    quiz_link: Optional[str] = None
    notification: Optional[str] = None
    duration: Optional[int] = None
    video_url: Optional[str] = None
    order_index: Optional[int] = None
    attachments: Optional[List[dict]] = None  # Added attachments field
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and len(v.strip()) < 1:
            raise ValueError("Title must not be empty")
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
    instructor: Optional[str] = None
    zoom_link: Optional[str] = None
    quiz_link: Optional[str] = None
    notification: Optional[str] = None
    duration: Optional[int] = None  # Duration in minutes
    video_url: Optional[str] = None
    order_index: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    module_id: UUID
    
    # Frontend compatibility fields (camelCase versions)
    zoomLink: Optional[str] = None
    quizLink: Optional[str] = None
    
    # Related objects
    attachments: Optional[List[dict]] = None  # Will be populated with attachment data
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm_with_attachments(cls, lesson):
        """Create LessonResponse with properly formatted attachments"""
        lesson_dict = {
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "instructor": lesson.instructor,
            "zoom_link": lesson.zoom_link,
            "quiz_link": lesson.quiz_link,
            "notification": lesson.notification,
            "duration": lesson.duration,
            "video_url": lesson.video_url,
            "order_index": lesson.order_index,
            "is_active": lesson.is_active,
            "created_at": lesson.created_at,
            "updated_at": lesson.updated_at,
            "module_id": lesson.module_id,
            "zoomLink": lesson.zoom_link,
            "quizLink": lesson.quiz_link,
            "attachments": [
                {
                    "id": str(att.id),
                    "name": att.name,
                    "url": att.url,
                    "file_type": att.file_type,
                    "file_size": att.file_size
                }
                for att in (lesson.attachments or [])
            ]
        }
        return cls(**lesson_dict)


# Lesson Attachment Schemas
class LessonAttachmentBase(BaseModel):
    name: str  # Changed from title to name to match frontend
    url: str   # Changed from file_url to url to match frontend and database
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    lesson_id: UUID
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Name must not be empty")
        return v.strip()


class LessonAttachmentCreate(LessonAttachmentBase):
    pass


class LessonAttachmentUpdate(BaseModel):
    name: Optional[str] = None  # Changed from title to name
    url: Optional[str] = None   # Changed from file_url to url
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and len(v.strip()) < 1:
            raise ValueError("Name must not be empty")
        return v.strip() if v else v


class LessonAttachmentResponse(LessonAttachmentBase):
    id: UUID
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
    course: Optional[dict] = None  # Will be populated with course data
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm_with_course(cls, enrollment):
        """Create UserEnrollmentResponse with course data"""
        enrollment_dict = {
            "id": enrollment.id,
            "user_id": enrollment.user_id,
            "course_id": enrollment.course_id,
            "is_completed": enrollment.is_completed,
            "progress_percentage": enrollment.progress_percentage,
            "enrolled_at": enrollment.enrolled_at,
            "last_accessed_at": enrollment.last_accessed_at,
            "completed_at": enrollment.completed_at,
            "course": {
                "id": str(enrollment.course.id),
                "title": enrollment.course.title,
                "description": enrollment.course.description,
                "thumbnail_url": enrollment.course.thumbnail_url,
                "difficulty_level": enrollment.course.difficulty_level,
                "estimated_duration": enrollment.course.estimated_duration,
                "is_published": enrollment.course.is_published,
                "price": enrollment.course.price,
                "instructor_id": enrollment.course.instructor_id
            } if enrollment.course else None
        }
        return cls(**enrollment_dict)


# Course List Response (for pagination)
class CourseListResponse(BaseModel):
    items: List[CourseResponse]
    total: int
    page: int
    size: int
    pages: int


# User Progress Schemas
class UserProgressResponse(BaseModel):
    lesson_id: UUID
    user_id: UUID
    is_completed: bool
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


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