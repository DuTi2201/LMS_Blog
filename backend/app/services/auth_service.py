from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from google.auth.transport import requests
from google.oauth2 import id_token

from ..core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    create_password_reset_token,
    verify_password_reset_token
)
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserUpdate, GoogleUserInfo, UserCreateByAdmin
from ..core.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        return self.db.query(User).filter(User.google_id == google_id).first()
    
    def get_user_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get user by email or username"""
        return self.db.query(User).filter(
            or_(User.email == identifier, User.username == identifier)
        ).first()
    
    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user"""
        # Check if email already exists
        if self.get_user_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists (only for local auth)
        if user_create.username and self.get_user_by_username(user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Validate auth provider requirements
        if user_create.auth_provider == "local" and not user_create.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required for local authentication"
            )
        
        if user_create.auth_provider == "google" and not user_create.google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google ID is required for Google authentication"
            )
        
        # Create new user
        hashed_password = None
        if user_create.password:
            hashed_password = get_password_hash(user_create.password)
        
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            role=user_create.role,
            is_active=user_create.is_active,
            avatar_url=user_create.avatar_url,
            bio=user_create.bio,
            auth_provider=user_create.auth_provider,
            google_id=user_create.google_id
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        user = self.get_user_by_email_or_username(identifier)

        if not user or not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated"
            )
        
        return user
    
    def create_tokens(self, user: User) -> dict:
        """Create access and refresh tokens for user"""
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Create new access token from refresh token"""
        try:
            payload = verify_token(refresh_token)
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user = self.get_user_by_id(int(user_id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is deactivated"
                )
            
            # Create new access token
            access_token = create_access_token(
                data={"sub": str(user.id), "type": "access"}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    def update_user(self, user_id: str, user_update: UserUpdate) -> User:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check email uniqueness if email is being updated
        if user_update.email and user_update.email != user.email:
            existing_user = self.get_user_by_email(user_update.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Check username uniqueness if username is being updated
        if user_update.username and user_update.username != user.username:
            existing_user = self.get_user_by_username(user_update.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Update user fields
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def deactivate_user(self, user_id: str) -> User:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Permanently delete user from database"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Delete user from database
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    def verify_user_email(self, user_id: str) -> User:
        """Mark user email as verified"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_verified = True
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def create_password_reset_request(self, email: str) -> str:
        """Create password reset token for user"""
        user = self.get_user_by_email(email)
        if not user:
            # Don't reveal if email exists or not for security
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="If the email exists, a password reset link has been sent"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated"
            )
        
        reset_token = create_password_reset_token(email)
        
        # TODO: Send email with reset token
        # This would typically involve sending an email with a link containing the token
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> User:
        """Reset user password using reset token"""
        try:
            email = verify_password_reset_token(token)
            user = self.get_user_by_email(email)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reset token"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User account is deactivated"
                )
            
            # Update password
            user.hashed_password = get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            return user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
    
    def get_current_user_from_token(self, token: str) -> User:
        """Get current user from access token"""
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user = self.get_user_by_id(int(user_id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is deactivated"
                )
            
            return user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """Get list of users with filtering"""
        query = self.db.query(User)
        
        # Filter by role
        if role is not None:
            query = query.filter(User.role == role)
        
        # Filter by active status
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Search by name or email
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.username.ilike(search_term)
                )
            )
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        return users
    
    def verify_google_token(self, token: str) -> GoogleUserInfo:
        """Verify Google ID token and extract user info"""
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            
            # Extract user information
            google_user_info = GoogleUserInfo(
                google_id=idinfo['sub'],
                email=idinfo['email'],
                full_name=idinfo.get('name', ''),
                avatar_url=idinfo.get('picture')
            )
            
            return google_user_info
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google token"
            )
    
    def authenticate_google_user(self, google_user_info: GoogleUserInfo) -> Optional[User]:
        """Authenticate user with Google OAuth"""
        # Check if user exists by email (admin must have added them)
        user = self.get_user_by_email(google_user_info.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Chưa đăng ký, vui lòng liên hệ admin"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated"
            )
        
        # Update user with Google info
        updated = False
        
        if not user.google_id:
            user.google_id = google_user_info.google_id
            user.auth_provider = "google"
            updated = True
        
        # Always update full_name and avatar_url from Google account
        if google_user_info.full_name and google_user_info.full_name != user.full_name:
            user.full_name = google_user_info.full_name
            updated = True
            
        if google_user_info.avatar_url and google_user_info.avatar_url != user.avatar_url:
            user.avatar_url = google_user_info.avatar_url
            updated = True
        
        if updated:
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        
        return user
    
    def create_user_by_admin(self, user_create: UserCreateByAdmin) -> User:
        """Create a new user by admin (for Google OAuth users)"""
        # Check if email already exists
        if self.get_user_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user for Google OAuth
        db_user = User(
            email=user_create.email,
            full_name=user_create.full_name or "",  # Default to empty string if not provided
            role=user_create.role,
            auth_provider="google",
            is_active=True,
            is_verified=True  # Google accounts are pre-verified
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # TODO: Assign courses if course_ids provided
        # This would require course enrollment logic
        
        return db_user