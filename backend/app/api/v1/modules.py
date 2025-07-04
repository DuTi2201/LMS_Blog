from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.learning import (
    ModuleCreate, ModuleUpdate, ModuleResponse
)
from ...services.learning_service import LearningService
from ..deps import (
    get_current_user, get_active_user, get_instructor_user,
    get_optional_current_user, get_learning_service
)
from ...models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=List[ModuleResponse])
def get_modules(
    course_id: Optional[UUID] = Query(None, description="Filter by course ID"),
    skip: int = Query(0, ge=0, description="Number of modules to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of modules to return"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get list of modules"""
    if course_id:
        # Check if course exists and user has access
        course = learning_service.get_course_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Check if user can view unpublished courses
        if not course.is_published:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )
            
            # Only instructor, admin, or enrolled users can view unpublished course modules
            if (current_user.id != course.instructor_id and 
                current_user.role != UserRole.ADMIN):
                # Check if user is enrolled
                enrollment = learning_service.get_user_enrollment(current_user.id, course_id)
                if not enrollment:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Course not found"
                    )
        
        modules = learning_service.get_modules_by_course(
            course_id=course_id,
            skip=skip,
            limit=limit
        )
    else:
        # Get all modules (admin only)
        if not current_user or current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        modules = learning_service.get_modules(
            skip=skip,
            limit=limit
        )
    
    return modules


@router.get("/{module_id}", response_model=ModuleResponse)
def get_module(
    module_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get module by ID"""
    module = learning_service.get_module_by_id(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check if user can view this module
    course = module.course
    if not course.is_published:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Only instructor, admin, or enrolled users can view unpublished course modules
        if (current_user.id != course.instructor_id and 
            current_user.role != UserRole.ADMIN):
            # Check if user is enrolled
            enrollment = learning_service.get_user_enrollment(current_user.id, course.id)
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Module not found"
                )
    
    return module


@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(
    module_create: ModuleCreate,
    current_user: User = Depends(get_instructor_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Create new module (Instructor+ only)"""
    # Check if course exists and user has permission
    course = learning_service.get_course_by_id(module_create.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check permissions: only course instructor or admin can create modules
    if (current_user.id != course.instructor_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create module in this course"
        )
    
    try:
        module = learning_service.create_module(module_create)
        return module
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{module_id}", response_model=ModuleResponse)
def update_module(
    module_id: UUID,
    module_update: ModuleUpdate,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Update module"""
    # Get the existing module
    existing_module = learning_service.get_module_by_id(module_id)
    if not existing_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check permissions: only course instructor or admin can update
    course = existing_module.course
    if (current_user.id != course.instructor_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this module"
        )
    
    try:
        module = learning_service.update_module(module_id, module_update)
        return module
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{module_id}")
def delete_module(
    module_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Delete module"""
    # Get the existing module
    existing_module = learning_service.get_module_by_id(module_id)
    if not existing_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check permissions: only course instructor or admin can delete
    course = existing_module.course
    if (current_user.id != course.instructor_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this module"
        )
    
    # Check if module has lessons
    if hasattr(existing_module, 'lessons') and existing_module.lessons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete module with lessons. Please delete lessons first."
        )
    
    success = learning_service.delete_module(module_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete module"
        )
    
    return {"message": "Module deleted successfully"}


@router.get("/{module_id}/lessons")
def get_module_lessons(
    module_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: Optional[User] = Depends(get_optional_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get lessons in a module"""
    module = learning_service.get_module_by_id(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check if user can view this module
    course = module.course
    if not course.is_published:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Only instructor, admin, or enrolled users can view unpublished course modules
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
    
    return {
        "module": module,
        "lessons": lessons,
        "total": len(lessons)
    }


@router.post("/{module_id}/reorder")
def reorder_module(
    module_id: UUID,
    new_order: int,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Reorder module within course"""
    # Get the existing module
    existing_module = learning_service.get_module_by_id(module_id)
    if not existing_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check permissions: only course instructor or admin can reorder
    course = existing_module.course
    if (current_user.id != course.instructor_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to reorder this module"
        )
    
    try:
        success = learning_service.reorder_module(module_id, new_order)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reorder module"
            )
        
        return {"message": "Module reordered successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{module_id}/progress")
def get_module_progress(
    module_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get current user's progress in module"""
    module = learning_service.get_module_by_id(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check if user is enrolled in the course
    course = module.course
    enrollment = learning_service.get_user_enrollment(current_user.id, course.id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not enrolled in this course"
        )
    
    progress = learning_service.get_user_module_progress(current_user.id, module_id)
    return progress


@router.get("/{module_id}/stats")
def get_module_stats(
    module_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get module statistics"""
    module = learning_service.get_module_by_id(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check permissions: only course instructor or admin can view stats
    course = module.course
    if (current_user.id != course.instructor_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view module statistics"
        )
    
    # Get course enrollments to calculate completion stats
    enrollments = learning_service.get_course_enrollments(course.id)
    
    stats = {
        "module_id": module_id,
        "title": module.title,
        "order_index": module.order_index,
        "total_lessons": len(module.lessons) if hasattr(module, 'lessons') else 0,
        "course_enrollments": len(enrollments),
        "estimated_duration": module.estimated_duration_minutes,
        "created_at": module.created_at,
        "updated_at": module.updated_at
    }
    
    return stats