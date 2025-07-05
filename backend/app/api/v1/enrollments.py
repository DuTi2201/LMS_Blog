from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.learning import UserEnrollmentResponse, UserEnrollmentCreate
from ...services.learning_service import LearningService
from ..deps import (
    get_current_user, get_admin_user,
    get_learning_service
)
from ...models.user import User, UserRole
from ...models.learning import UserEnrollment

router = APIRouter()


@router.post("/", response_model=UserEnrollmentResponse)
def create_enrollment(
    enrollment_data: UserEnrollmentCreate,
    current_user: User = Depends(get_admin_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Create new enrollment (Admin only)"""
    try:
        enrollment = learning_service.enroll_user_in_course(
            user_id=enrollment_data.user_id,
            course_id=enrollment_data.course_id
        )
        return enrollment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}/{course_id}")
def delete_enrollment(
    user_id: str,
    course_id: str,
    current_user: User = Depends(get_admin_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Delete enrollment (Admin only)"""
    try:
        success = learning_service.unenroll_user_from_course(
            user_id=user_id,
            course_id=course_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        return {"message": "Enrollment deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/user/{user_id}", response_model=List[UserEnrollmentResponse])
def get_user_enrollments(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get user enrollments"""
    # Users can view their own enrollments or admins can view any user's enrollments
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    enrollments = learning_service.get_user_enrollments(
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    
    # Convert to response with course data
    return [UserEnrollmentResponse.from_orm_with_course(enrollment) for enrollment in enrollments]


@router.get("/course/{course_id}", response_model=List[UserEnrollmentResponse])
def get_course_enrollments(
    course_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_admin_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get course enrollments (Admin only)"""
    enrollments = learning_service.get_course_enrollments(
        course_id=course_id,
        skip=skip,
        limit=limit
    )
    return enrollments