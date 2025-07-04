from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
import uuid
from ..core.database import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    USER = "user"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)  # Optional for Google OAuth
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Optional for Google OAuth
    role = Column(String(50), default="user", nullable=False)  # admin, user
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Google OAuth fields
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    auth_provider = Column(String(50), default="local", nullable=False)  # local, google
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    blog_posts = relationship("BlogPost", back_populates="author", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="instructor", cascade="all, delete-orphan")
    enrollments = relationship("UserEnrollment", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"