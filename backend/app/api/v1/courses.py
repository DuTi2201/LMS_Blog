from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...core.database import get_db
from ...schemas.learning import (
    CourseCreate, CourseUpdate, CourseResponse,
    UserEnrollmentCreate, UserEnrollmentResponse,
    CourseSearchParams, ModuleResponse, ModuleCreate
)
from ...services.learning_service import LearningService
from ..deps import (
    get_current_user, get_active_user, get_instructor_user,
    get_optional_current_user, get_learning_service
)
from ...models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=List[CourseResponse])
def get_courses(
    skip: int = Query(0, ge=0, description="Number of courses to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of courses to return"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    instructor_id: Optional[int] = Query(None, description="Filter by instructor ID"),
    is_published: Optional[bool] = Query(True, description="Filter by published status"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get list of courses with filtering and search"""
    # If user is not authenticated or not admin/instructor, only show published courses
    if not current_user or current_user.role == UserRole.USER:
        is_published = True
    
    search_params = CourseSearchParams(
        q=search,
        instructor_id=instructor_id,
        is_published=is_published,
        difficulty_level=difficulty_level,
        page=skip//limit + 1,
        size=limit
    )
    
    courses, total = learning_service.get_courses(search_params)
    
    return courses


@router.get("/my-courses", response_model=List[CourseResponse])
def get_my_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get current user's created courses (for instructors)"""
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot create courses"
        )
    
    courses = learning_service.get_courses_by_instructor(
        instructor_id=current_user.id,
        skip=skip,
        limit=limit,
        is_published=is_published
    )
    return courses


@router.get("/enrolled", response_model=List[CourseResponse])
def get_enrolled_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get current user's enrolled courses"""
    enrollments = learning_service.get_user_enrollments(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    # Extract courses from enrollments
    courses = [enrollment.course for enrollment in enrollments]
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get course by ID"""
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
        
        # Only instructor, admin can view unpublished courses
        if (current_user.id != course.instructor_id and 
            current_user.role != UserRole.ADMIN):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
    
    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_create: CourseCreate,
    current_user: User = Depends(get_instructor_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Create new course (Instructor+ only)"""
    try:
        course = learning_service.create_course(course_create, instructor_id=current_user.id)
        return course
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: UUID,
    course_update: CourseUpdate,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Update course"""
    course = learning_service.update_course(course_id, course_update, current_user.id)
    return course


@router.delete("/{course_id}")
def delete_course(
    course_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Delete course"""
    success = learning_service.delete_course(course_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete course"
        )
    
    return {"message": "Course deleted successfully"}


@router.post("/{course_id}/enroll", response_model=UserEnrollmentResponse)
def enroll_in_course(
    course_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Enroll current user in course"""
    enrollment_create = UserEnrollmentCreate(course_id=course_id)
    enrollment = learning_service.enroll_user(
        enrollment_create, user_id=current_user.id
    )
    return enrollment


@router.delete("/{course_id}/enroll")
def unenroll_from_course(
    course_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Unenroll current user from course"""
    success = learning_service.unenroll_user(course_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unenroll from course"
        )
    
    return {"message": "Successfully unenrolled from course"}


@router.get("/{course_id}/enrollments", response_model=List[UserEnrollmentResponse])
def get_course_enrollments(
    course_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get course enrollments (Instructor/Admin only)"""
    enrollments = learning_service.get_course_enrollments(
        course_id=course_id,
        skip=skip,
        limit=limit
    )
    
    return enrollments


@router.get("/{course_id}/progress")
def get_course_progress(
    course_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get current user's progress in course"""
    progress = learning_service.get_user_course_progress(current_user.id, course_id)
    return progress


@router.post("/{course_id}/publish")
def publish_course(
    course_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Publish course"""
    course_update = CourseUpdate(is_published=True)
    course = learning_service.update_course(course_id, course_update, current_user.id)
    
    return {"message": "Course published successfully"}


@router.post("/{course_id}/unpublish")
def unpublish_course(
    course_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Unpublish course"""
    course_update = CourseUpdate(is_published=False)
    course = learning_service.update_course(course_id, course_update, current_user.id)
    
    return {"message": "Course unpublished successfully"}


@router.get("/{course_id}/stats")
def get_course_stats(
    course_id: UUID,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get course statistics"""
    course = learning_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check permissions: only instructor or admin can view stats
    if (current_user.id != course.instructor_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view course statistics"
        )
    
    enrollments = learning_service.get_course_enrollments(course_id)
    
    stats = {
        "course_id": course_id,
        "title": course.title,
        "is_published": course.is_published,
        "total_enrollments": len(enrollments),
        "active_enrollments": len([e for e in enrollments if e.is_active]),
        "completed_enrollments": len([e for e in enrollments if e.completion_percentage == 100]),
        "average_progress": sum([e.completion_percentage for e in enrollments]) / len(enrollments) if enrollments else 0,
        "total_modules": len(course.modules) if hasattr(course, 'modules') else 0,
        "total_lessons": sum([len(module.lessons) for module in course.modules]) if hasattr(course, 'modules') else 0,
        "created_at": course.created_at,
        "updated_at": course.updated_at
    }
    
    return stats


@router.get("/{course_id}/modules", response_model=List[ModuleResponse])
def get_course_modules(
    course_id: UUID,
    skip: int = Query(0, ge=0, description="Number of modules to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of modules to return"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Get modules for a specific course"""
    # Check if course exists
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
    
    # Get modules for the course
    modules = learning_service.get_modules_by_course_id(
        course_id=course_id,
        skip=skip,
        limit=limit
    )
    
    return modules


@router.post("/{course_id}/modules", response_model=ModuleResponse)
def create_course_module(
    course_id: UUID,
    module_data: ModuleCreate,
    current_user: User = Depends(get_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """Create a new module for a course (Instructor/Admin only)"""
    # Check if course exists
    course = learning_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check permissions: only instructor or admin can create modules
    if (current_user.id != course.instructor_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create modules for this course"
        )
    
    try:
        module = learning_service.create_module(course_id, module_data)
        return module
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )