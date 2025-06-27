from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail = Column(String(500), nullable=True)
    difficulty_level = Column(String(20), default="beginner", nullable=False)  # beginner, intermediate, advanced
    estimated_duration = Column(Integer, nullable=True)  # in hours
    is_published = Column(Boolean, default=False, nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan", order_by="Module.order_index")
    enrollments = relationship("UserEnrollment", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}', difficulty='{self.difficulty_level}')>"


class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order_index")
    
    def __repr__(self):
        return f"<Module(id={self.id}, title='{self.title}', course_id={self.course_id})>"


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    lesson_type = Column(String(20), default="text", nullable=False)  # text, video, quiz, assignment
    video_url = Column(String(500), nullable=True)
    duration = Column(Integer, nullable=True)  # in minutes
    order_index = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    is_free = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    
    # Relationships
    module = relationship("Module", back_populates="lessons")
    attachments = relationship("LessonAttachment", back_populates="lesson", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lesson(id={self.id}, title='{self.title}', type='{self.lesson_type}')>"


class LessonAttachment(Base):
    __tablename__ = "lesson_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    
    # Relationships
    lesson = relationship("Lesson", back_populates="attachments")
    
    def __repr__(self):
        return f"<LessonAttachment(id={self.id}, filename='{self.filename}', lesson_id={self.lesson_id})>"


class UserEnrollment(Base):
    __tablename__ = "user_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
    def __repr__(self):
        return f"<UserEnrollment(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, progress={self.progress_percentage}%)>"


class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent = Column(Integer, default=0, nullable=False)  # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    
    # Relationships
    user = relationship("User")
    lesson = relationship("Lesson")
    
    def __repr__(self):
        return f"<UserProgress(id={self.id}, user_id={self.user_id}, lesson_id={self.lesson_id}, completed={self.is_completed})>"