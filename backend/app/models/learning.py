from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    difficulty_level = Column(String(20), default="beginner", nullable=False)  # beginner, intermediate, advanced
    estimated_duration = Column(Integer, nullable=True)  # in hours
    is_published = Column(Boolean, default=False, nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    instructor = relationship("User", back_populates="courses")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan", order_by="Module.order_index")
    enrollments = relationship("UserEnrollment", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}', difficulty='{self.difficulty_level}')>"


class Module(Base):
    __tablename__ = "modules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order_index")
    
    def __repr__(self):
        return f"<Module(id={self.id}, title='{self.title}', course_id={self.course_id})>"


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    lesson_date = Column(DateTime(timezone=True), nullable=True)
    instructor_name = Column(String(255), nullable=True)
    zoom_link = Column(String(500), nullable=True)
    quiz_link = Column(String(500), nullable=True)
    notification = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False)
    
    # Relationships
    module = relationship("Module", back_populates="lessons")
    attachments = relationship("LessonAttachment", back_populates="lesson", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lesson(id={self.id}, title='{self.title}', type='{self.lesson_type}')>"


class LessonAttachment(Base):
    __tablename__ = "lesson_attachments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    file_type = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    
    # Relationships
    lesson = relationship("Lesson", back_populates="attachments")
    
    def __repr__(self):
        return f"<LessonAttachment(id={self.id}, filename='{self.filename}', lesson_id={self.lesson_id})>"


class UserEnrollment(Base):
    __tablename__ = "user_enrollments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
    def __repr__(self):
        return f"<UserEnrollment(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, progress={self.progress_percentage}%)>"


class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent = Column(Integer, default=0, nullable=False)  # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    
    # Relationships
    user = relationship("User")
    lesson = relationship("Lesson")
    
    def __repr__(self):
        return f"<UserProgress(id={self.id}, user_id={self.user_id}, lesson_id={self.lesson_id}, completed={self.is_completed})>"