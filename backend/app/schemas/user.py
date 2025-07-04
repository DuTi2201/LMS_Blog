from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: str
    role: str = "user"
    is_active: bool = True
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    auth_provider: str = "local"
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ["admin", "user", "instructor"]:
            raise ValueError("Role must be either 'admin', 'user', or 'instructor'")
        return v
    
    @field_validator("auth_provider")
    @classmethod
    def validate_auth_provider(cls, v):
        if v not in ["local", "google"]:
            raise ValueError("Auth provider must be either 'local' or 'google'")
        return v


class UserCreate(UserBase):
    password: Optional[str] = None
    google_id: Optional[str] = None
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v
    
    def model_validate(self, values):
        # Ensure either password (for local auth) or google_id (for Google auth) is provided
        if values.get('auth_provider') == 'local' and not values.get('password'):
            raise ValueError("Password is required for local authentication")
        if values.get('auth_provider') == 'google' and not values.get('google_id'):
            raise ValueError("Google ID is required for Google authentication")
        return values


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v is not None and v not in ["admin", "user", "instructor"]:
            raise ValueError("Role must be either 'admin', 'user', or 'instructor'")
        return v
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserResponse(UserBase):
    id: UUID
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    google_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


# Google OAuth schemas
class GoogleTokenRequest(BaseModel):
    token: str  # Google ID token


class GoogleUserInfo(BaseModel):
    google_id: str
    email: EmailStr
    full_name: str
    avatar_url: Optional[str] = None


class UserCreateByAdmin(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "user"
    course_ids: Optional[list[UUID]] = []
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ["admin", "user", "instructor"]:
            raise ValueError("Role must be either 'admin', 'user', or 'instructor'")
        return v