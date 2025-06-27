from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.user import (
    UserCreate, UserResponse, UserLogin, Token,
    PasswordReset, PasswordResetConfirm
)
from ...services.auth_service import AuthService
from ..deps import get_current_user, get_auth_service
from ...models.user import User

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_create: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    try:
        user = auth_service.create_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login(
    user_login: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user and return access token"""
    user = auth_service.authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Generate tokens
    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token using refresh token"""
    try:
        new_access_token = auth_service.refresh_access_token(refresh_token)
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user (client should discard tokens)"""
    # In a more sophisticated implementation, you might want to:
    # 1. Blacklist the token
    # 2. Store logout timestamp
    # 3. Clear any server-side sessions
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/verify-email")
def verify_email(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify user email with token"""
    try:
        success = auth_service.verify_email(token)
        if success:
            return {"message": "Email verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/resend-verification")
def resend_verification_email(
    email: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Resend email verification"""
    try:
        success = auth_service.send_verification_email(email)
        if success:
            return {"message": "Verification email sent"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/forgot-password")
def forgot_password(
    password_reset: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request password reset"""
    try:
        success = auth_service.request_password_reset(password_reset.email)
        # Always return success message for security reasons
        # (don't reveal if email exists or not)
        return {"message": "If the email exists, a password reset link has been sent"}
    except Exception:
        # Log the error but don't expose it to the user
        return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
def reset_password(
    password_reset_confirm: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset password with token"""
    try:
        success = auth_service.reset_password(
            password_reset_confirm.token,
            password_reset_confirm.new_password
        )
        if success:
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change user password"""
    # Verify current password
    if not auth_service.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    try:
        # Update password
        success = auth_service.update_user_password(current_user.id, new_password)
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )