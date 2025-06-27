from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: str = "user"
    is_active: bool = True
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ["admin", "user"]:
            raise ValueError("Role must be either 'admin' or 'user'")
        return v


class UserCreate(UserBase):
    password: str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


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
        if v is not None and v not in ["admin", "user"]:
            raise ValueError("Role must be either 'admin' or 'user'")
        return v
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserResponse(UserBase):
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str  # Can be username or email
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


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