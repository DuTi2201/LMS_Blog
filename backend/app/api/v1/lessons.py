from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.learning import (
    LessonCreate, LessonUpdate, LessonResponse,
    LessonAttachmentCreate, LessonAttachmentResponse,
    UserProgressResponse
)
from ...services.learning_service import LearningService
from ...services.file_service import FileService
from ..deps import (
    get_current_user, get_active_user, get_instructor_user,
    get_optional_current_user, get_learning_service, get_file_service
)
from ...models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=List[LessonResponse])
def get_lessons(
    module_id: Optional[UUID] = Query(None, description="Filter by module ID"),
    skip: int = Query(0, ge=0, description="Number of lessons to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of lessons to return"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get list of lessons"""
    if module_id:
        # Check if module exists and user has access
        module = learning_service.get_module_by_id(module_id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Check if user can view unpublished course lessons
        course = module.course
        if not course.is_published:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Module not found"
                )
            
            # Only instructor, admin, or enrolled users can view unpublished course lessons
            if (current_user.id != course.instructor_id and 
                current_user.role != UserRole.ADMIN):
                # Check if user is enrolled
                enrollment = learning_service.get_user_enrollment(current_user.id, course.id)
                if not enrollment:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Module not found"
                    )
        
        lessons = learning_service.get_lessons_by_module(
            module_id=module_id,
            skip=skip,
            limit=limit
        )
    else:
        # Get all lessons (admin only)
        if not current_user or current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        lessons = learning_service.get_lessons(
            skip=skip,
            limit=limit
        )
    
    return [LessonResponse.from_orm_with_attachments(lesson) for lesson in lessons]


@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get lesson by ID"""
    lesson = learning_service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check if user can view this lesson
    module = lesson.module
    course = module.course
    if not course.is_published:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Only instructor, admin, or enrolled users can view unpublished course lessons
        if (current_user.id != course.instructor_id and 
            current_user.role != UserRole.ADMIN):
            # Check if user is enrolled
            enrollment = learning_service.get_user_enrollment(current_user.id, course.id)
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lesson not found"
                )
    
    return LessonResponse.from_orm_with_attachments(lesson)


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    lesson_create: LessonCreate,
    module_id: UUID = Query(..., description="Module ID to create lesson in"),
    current_user: User = Depends(get_instructor_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Create new lesson (Instructor+ only)"""
    try:
        lesson = learning_service.create_lesson(
            lesson_create=lesson_create,
            module_id=module_id,
            user_id=current_user.id
        )
        return LessonResponse.from_orm_with_attachments(lesson)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: UUID,
    lesson_update: LessonUpdate,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Update lesson"""
    try:
        lesson = learning_service.update_lesson(
            lesson_id=lesson_id,
            lesson_update=lesson_update,
            user_id=current_user.id
        )
        return LessonResponse.from_orm_with_attachments(lesson)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Delete lesson"""
    success = learning_service.delete_lesson(
        lesson_id=lesson_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete lesson"
        )
    
    return {"message": "Lesson deleted successfully"}


@router.post("/{lesson_id}/reorder")
def reorder_lesson(
    lesson_id: UUID,
    new_order: int,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Reorder lesson within module"""
    # Get the existing lesson
    existing_lesson = learning_service.get_lesson_by_id(lesson_id)
    if not existing_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check permissions: only course instructor or admin can reorder
    module = existing_lesson.module
    course = module.course
    if (current_user.id != course.instructor_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to reorder this lesson"
        )
    
    try:
        success = learning_service.reorder_lesson(lesson_id, new_order)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reorder lesson"
            )
        
        return {"message": "Lesson reordered successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{lesson_id}/complete")
def complete_lesson(
    lesson_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Mark lesson as completed for current user"""
    progress = learning_service.mark_lesson_complete(
        lesson_id=lesson_id,
        user_id=current_user.id
    )
    
    return progress


@router.delete("/{lesson_id}/complete")
def uncomplete_lesson(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Mark lesson as uncompleted"""
    success = learning_service.uncomplete_lesson(
        lesson_id=lesson_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to uncomplete lesson"
        )
    
    return {"message": "Lesson uncompleted successfully"}


# Lesson Attachments
@router.get("/{lesson_id}/attachments", response_model=List[LessonAttachmentResponse])
def get_lesson_attachments(
    lesson_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get lesson attachments"""
    lesson = learning_service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check if user can view this lesson
    module = lesson.module
    course = module.course
    if not course.is_published:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Only instructor, admin, or enrolled users can view unpublished course lessons
        if (current_user.id != course.instructor_id and 
            current_user.role != UserRole.ADMIN):
            # Check if user is enrolled
            enrollment = learning_service.get_user_enrollment(current_user.id, course.id)
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lesson not found"
                )
    
    attachments = learning_service.get_lesson_attachments(lesson_id)
    return attachments


@router.post("/{lesson_id}/attachments", response_model=LessonAttachmentResponse, status_code=status.HTTP_201_CREATED)
def create_lesson_attachment(
    lesson_id: UUID,
    attachment_create: LessonAttachmentCreate,
    current_user: User = Depends(get_instructor_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Create lesson attachment (Instructor+ only)"""
    try:
        attachment = learning_service.create_lesson_attachment(
            attachment_create=attachment_create,
            lesson_id=lesson_id,
            user_id=current_user.id
        )
        return attachment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{lesson_id}/attachments/upload")
async def upload_lesson_attachment(
    lesson_id: UUID,
    file: UploadFile = File(...),
    title: Optional[str] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_instructor_user),
    learning_service: LearningService = Depends(get_learning_service),
    file_service: FileService = Depends(get_file_service)
):
    """Upload lesson attachment file (Instructor+ only)"""
    # Check if lesson exists and user has permission
    lesson = learning_service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check permissions: only course instructor or admin can upload attachments
    module = lesson.module
    course = module.course
    if (current_user.id != course.instructor_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to upload attachment for this lesson"
        )
    
    try:
        # Upload file
        file_info = await file_service.upload_attachment(file)
        
        # Create attachment record
        attachment_create = LessonAttachmentCreate(
            name=title or file.filename,
            url=file_info["file_url"],
            file_type=file_info["file_type"],
            file_size=file_info["file_size"]
        )
        
        attachment = learning_service.create_lesson_attachment(
            attachment_create=attachment_create,
            lesson_id=lesson_id,
            user_id=current_user.id
        )
        return attachment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload attachment: {str(e)}"
        )


@router.delete("/attachments/{attachment_id}")
async def delete_lesson_attachment(
    attachment_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service),
    file_service: FileService = Depends(get_file_service)
):
    """Delete lesson attachment"""
    # Get the existing attachment
    attachment = learning_service.get_lesson_attachment_by_id(attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # Check permissions: only course instructor or admin can delete
    lesson = attachment.lesson
    module = lesson.module
    course = module.course
    if (current_user.id != course.instructor_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this attachment"
        )
    
    try:
        # Delete file from storage
        if attachment.url:
            await file_service.delete_file(attachment.url)
        
        # Delete attachment record
        success = learning_service.delete_lesson_attachment(
            attachment_id=attachment_id,
            user_id=current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete attachment"
            )
        
        return {"message": "Attachment deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete attachment: {str(e)}"
        )


@router.get("/{lesson_id}/progress", response_model=UserProgressResponse)
def get_lesson_progress(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get user's progress for a specific lesson"""
    progress = learning_service.get_user_lesson_progress(
        user_id=current_user.id,
        lesson_id=lesson_id
    )
    
    if not progress:
        # Return default progress if none exists
        return UserProgressResponse(
            id=None,
            user_id=current_user.id,
            lesson_id=lesson_id,
            is_completed=False,
            progress_percentage=0.0,
            completed_at=None,
            last_accessed_at=None
        )
    
    return progress