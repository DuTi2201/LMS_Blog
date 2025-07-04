from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.user import UserResponse, UserUpdate, UserCreate
from ...schemas.learning import UserEnrollmentResponse
from ...services.auth_service import AuthService
from ...services.learning_service import LearningService
from ..deps import (
    get_current_user, get_active_user, get_admin_user,
    get_auth_service, get_learning_service
)
from ...models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    current_user: User = Depends(get_admin_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get list of users (Admin only)"""
    users = auth_service.get_users(
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
        search=search
    )
    return users


@router.post("/", response_model=UserResponse)
def create_user(
    user_create: UserCreate,
    current_user: User = Depends(get_admin_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Create new user (Admin only)"""
    try:
        new_user = auth_service.create_user(user_create)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update current user profile"""
    try:
        updated_user = auth_service.update_user(current_user.id, user_update)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/instructors", response_model=List[UserResponse])
def get_instructors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search by name"),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get list of instructors"""
    instructors = auth_service.get_users(
        skip=skip,
        limit=limit,
        role=UserRole.INSTRUCTOR,
        is_active=True,
        search=search
    )
    return instructors


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user by ID"""
    # Users can view their own profile or admins can view any profile
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_admin_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update user (Admin only)"""
    try:
        updated_user = auth_service.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}")
def deactivate_user(
    user_id: str,
    current_user: User = Depends(get_admin_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Deactivate user (Admin only)"""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    success = auth_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deactivated successfully"}


@router.post("/{user_id}/activate")
def activate_user(
    user_id: str,
    current_user: User = Depends(get_admin_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Activate user (Admin only)"""
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active"
        )
    
    # Reactivate user by updating is_active status
    user_update = UserUpdate(is_active=True)
    updated_user = auth_service.update_user(user_id, user_update)
    
    return {"message": "User activated successfully"}


@router.get("/{user_id}/enrollments", response_model=List[UserEnrollmentResponse])
def get_user_enrollments_for_user(
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
    return enrollments


@router.post("/{user_id}/change-role")
def change_user_role(
    user_id: str,
    new_role: UserRole,
    current_user: User = Depends(get_admin_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change user role (Admin only)"""
    if current_user.id == user_id and new_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role"
        )
    
    user_update = UserUpdate(role=new_role)
    updated_user = auth_service.update_user(user_id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"User role changed to {new_role.value} successfully"}


@router.get("/{user_id}/stats")
def get_user_stats(
    user_id: str,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user statistics"""
    # Users can view their own stats or admins can view any user's stats
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user statistics (this would typically involve querying related tables)
    stats = {
        "user_id": user_id,
        "total_courses_enrolled": len(user.enrollments) if hasattr(user, 'enrollments') else 0,
        "total_blog_posts": len(user.blog_posts) if hasattr(user, 'blog_posts') else 0,
        "account_created": user.created_at,
        "last_login": user.last_login_at,
        "is_active": user.is_active,
        "role": user.role
    }
    
    return stats


@router.get("/{user_id}/enrollments", response_model=List[UserEnrollmentResponse])
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
    return enrollments