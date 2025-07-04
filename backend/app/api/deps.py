from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Optional

from ..core.database import get_db
from ..core.config import settings
from ..models.user import User, UserRole
from ..services.auth_service import AuthService

# Security scheme
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (alias for get_current_user)"""
    return current_user


def get_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get active user (alias for get_current_user)"""
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user and verify admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user


def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get admin user (alias for get_current_admin_user)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user


def get_current_instructor_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user and verify instructor or admin role"""
    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Instructor or Admin role required."
        )
    return current_user


def get_instructor_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get instructor user (alias for get_current_instructor_user)"""
    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Instructor or Admin role required."
        )
    return current_user


def get_optional_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)
) -> Optional[User]:
    """Get current user if token is provided, otherwise return None"""
    if not credentials:
        return None
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    # Get user from database
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    if user is None or not user.is_active:
        return None
    
    return user


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get AuthService instance"""
    return AuthService(db)


def get_blog_service(db: Session = Depends(get_db)):
    """Get BlogService instance"""
    from ..services.blog_service import BlogService
    return BlogService(db)


def get_learning_service(db: Session = Depends(get_db)):
    """Get LearningService instance"""
    from ..services.learning_service import LearningService
    return LearningService(db)


def get_file_service():
    """Get FileService instance"""
    from ..services.file_service import FileService
    return FileService()


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def check_user_permissions(user: User, required_roles: list) -> bool:
    """Check if user has required roles"""
    return user.role in required_roles


def require_roles(roles: list):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not check_user_permissions(current_user, roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required roles: {', '.join(roles)}"
            )
        return current_user
    return role_checker