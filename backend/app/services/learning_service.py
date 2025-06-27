from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, asc, func
from fastapi import HTTPException, status
from datetime import datetime

from ..models.learning import (
    Course, Module, Lesson, LessonAttachment,
    UserEnrollment, UserProgress
)
from ..models.user import User
from ..schemas.learning import (
    CourseCreate, CourseUpdate, CourseSearchParams,
    ModuleCreate, ModuleUpdate,
    LessonCreate, LessonUpdate,
    LessonAttachmentCreate, LessonAttachmentUpdate,
    UserEnrollmentCreate
)


class LearningService:
    def __init__(self, db: Session):
        self.db = db
    
    # Course Methods
    def create_course(self, course_create: CourseCreate, instructor_id: int) -> Course:
        """Create a new course"""
        db_course = Course(
            title=course_create.title,
            description=course_create.description,
            short_description=course_create.short_description,
            thumbnail_url=course_create.thumbnail_url,
            difficulty_level=course_create.difficulty_level,
            estimated_duration=course_create.estimated_duration,
            is_published=course_create.is_published,
            price=course_create.price,
            instructor_id=instructor_id
        )
        
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)
        
        return db_course
    
    def get_courses(self, search_params: CourseSearchParams) -> Tuple[List[Course], int]:
        """Get courses with search and pagination"""
        query = self.db.query(Course).options(
            joinedload(Course.instructor),
            joinedload(Course.modules).joinedload(Module.lessons)
        )
        
        # Apply filters
        if search_params.q:
            search_term = f"%{search_params.q}%"
            query = query.filter(
                Course.title.ilike(search_term) |
                Course.description.ilike(search_term)
            )
        
        if search_params.instructor_id:
            query = query.filter(Course.instructor_id == search_params.instructor_id)
        
        if search_params.difficulty_level:
            query = query.filter(Course.difficulty_level == search_params.difficulty_level)
        
        if search_params.is_published is not None:
            query = query.filter(Course.is_published == search_params.is_published)
        
        if search_params.min_price is not None:
            query = query.filter(Course.price >= search_params.min_price)
        
        if search_params.max_price is not None:
            query = query.filter(Course.price <= search_params.max_price)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if search_params.sort_order == "desc":
            order_func = desc
        else:
            order_func = asc
        
        if search_params.sort_by == "title":
            query = query.order_by(order_func(Course.title))
        elif search_params.sort_by == "price":
            query = query.order_by(order_func(Course.price))
        elif search_params.sort_by == "enrollment_count":
            query = query.order_by(order_func(Course.enrollment_count))
        elif search_params.sort_by == "updated_at":
            query = query.order_by(order_func(Course.updated_at))
        else:  # default to created_at
            query = query.order_by(order_func(Course.created_at))
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.size
        courses = query.offset(offset).limit(search_params.size).all()
        
        return courses, total
    
    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """Get course by ID with full details"""
        return self.db.query(Course).options(
            joinedload(Course.instructor),
            joinedload(Course.modules).joinedload(Module.lessons).joinedload(Lesson.attachments)
        ).filter(Course.id == course_id).first()
    
    def update_course(self, course_id: int, course_update: CourseUpdate, user_id: int) -> Course:
        """Update course"""
        course = self.get_course_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Check if user is the instructor or admin
        if course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this course"
            )
        
        update_data = course_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(course, field, value)
        
        course.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(course)
        
        return course
    
    def delete_course(self, course_id: int, user_id: int) -> bool:
        """Delete course"""
        course = self.get_course_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Check if user is the instructor or admin
        if course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this course"
            )
        
        # Check if course has enrollments
        enrollment_count = self.db.query(UserEnrollment).filter(
            UserEnrollment.course_id == course_id
        ).count()
        
        if enrollment_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete course. It has {enrollment_count} enrollments"
            )
        
        self.db.delete(course)
        self.db.commit()
        
        return True
    
    def get_popular_courses(self, limit: int = 10) -> List[Course]:
        """Get most popular courses by enrollment count"""
        return self.db.query(Course).options(
            joinedload(Course.instructor)
        ).filter(
            Course.is_published == True
        ).order_by(
            desc(Course.enrollment_count)
        ).limit(limit).all()
    
    def get_recent_courses(self, limit: int = 10) -> List[Course]:
        """Get most recent published courses"""
        return self.db.query(Course).options(
            joinedload(Course.instructor)
        ).filter(
            Course.is_published == True
        ).order_by(
            desc(Course.created_at)
        ).limit(limit).all()
    
    # Module Methods
    def create_module(self, module_create: ModuleCreate, course_id: int, user_id: int) -> Module:
        """Create a new module"""
        # Check if course exists and user has permission
        course = self.get_course_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        if course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add modules to this course"
            )
        
        # Get next order number
        max_order = self.db.query(func.max(Module.order_index)).filter(
            Module.course_id == course_id
        ).scalar() or 0
        
        db_module = Module(
            title=module_create.title,
            description=module_create.description,
            order_index=max_order + 1,
            course_id=course_id
        )
        
        self.db.add(db_module)
        self.db.commit()
        self.db.refresh(db_module)
        
        return db_module
    
    def get_module_by_id(self, module_id: int) -> Optional[Module]:
        """Get module by ID with lessons"""
        return self.db.query(Module).options(
            joinedload(Module.course),
            joinedload(Module.lessons).joinedload(Lesson.attachments)
        ).filter(Module.id == module_id).first()
    
    def update_module(self, module_id: int, module_update: ModuleUpdate, user_id: int) -> Module:
        """Update module"""
        module = self.get_module_by_id(module_id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Check if user is the course instructor or admin
        if module.course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this module"
            )
        
        update_data = module_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(module, field, value)
        
        module.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(module)
        
        return module
    
    def delete_module(self, module_id: int, user_id: int) -> bool:
        """Delete module"""
        module = self.get_module_by_id(module_id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Check if user is the course instructor or admin
        if module.course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this module"
            )
        
        self.db.delete(module)
        self.db.commit()
        
        return True
    
    def reorder_modules(self, course_id: int, module_orders: List[dict], user_id: int) -> List[Module]:
        """Reorder modules in a course"""
        # Check if course exists and user has permission
        course = self.get_course_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        if course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to reorder modules in this course"
            )
        
        # Update order for each module
        for order_data in module_orders:
            module_id = order_data.get("module_id")
            new_order = order_data.get("order_index")
            
            module = self.db.query(Module).filter(
                and_(
                    Module.id == module_id,
                    Module.course_id == course_id
                )
            ).first()
            
            if module:
                module.order_index = new_order
                module.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Return updated modules
        return self.db.query(Module).filter(
            Module.course_id == course_id
        ).order_by(Module.order_index).all()
    
    # Lesson Methods
    def create_lesson(self, lesson_create: LessonCreate, module_id: int, user_id: int) -> Lesson:
        """Create a new lesson"""
        # Check if module exists and user has permission
        module = self.get_module_by_id(module_id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        if module.course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add lessons to this module"
            )
        
        # Get next order number
        max_order = self.db.query(func.max(Lesson.order_index)).filter(
            Lesson.module_id == module_id
        ).scalar() or 0
        
        db_lesson = Lesson(
            title=lesson_create.title,
            content=lesson_create.content,
            lesson_type=lesson_create.lesson_type,
            video_url=lesson_create.video_url,
            duration=lesson_create.duration,
            order_index=max_order + 1,
            is_preview=lesson_create.is_preview,
            module_id=module_id
        )
        
        self.db.add(db_lesson)
        self.db.commit()
        self.db.refresh(db_lesson)
        
        return db_lesson
    
    def get_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        """Get lesson by ID with attachments"""
        return self.db.query(Lesson).options(
            joinedload(Lesson.module).joinedload(Module.course),
            joinedload(Lesson.attachments)
        ).filter(Lesson.id == lesson_id).first()
    
    def update_lesson(self, lesson_id: int, lesson_update: LessonUpdate, user_id: int) -> Lesson:
        """Update lesson"""
        lesson = self.get_lesson_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Check if user is the course instructor or admin
        if lesson.module.course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this lesson"
            )
        
        update_data = lesson_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(lesson, field, value)
        
        lesson.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(lesson)
        
        return lesson
    
    def delete_lesson(self, lesson_id: int, user_id: int) -> bool:
        """Delete lesson"""
        lesson = self.get_lesson_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Check if user is the course instructor or admin
        if lesson.module.course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this lesson"
            )
        
        self.db.delete(lesson)
        self.db.commit()
        
        return True
    
    # Lesson Attachment Methods
    def create_lesson_attachment(self, attachment_create: LessonAttachmentCreate, lesson_id: int, user_id: int) -> LessonAttachment:
        """Create a new lesson attachment"""
        # Check if lesson exists and user has permission
        lesson = self.get_lesson_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        if lesson.module.course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add attachments to this lesson"
            )
        
        db_attachment = LessonAttachment(
            filename=attachment_create.filename,
            file_url=attachment_create.file_url,
            file_type=attachment_create.file_type,
            file_size=attachment_create.file_size,
            lesson_id=lesson_id
        )
        
        self.db.add(db_attachment)
        self.db.commit()
        self.db.refresh(db_attachment)
        
        return db_attachment
    
    def delete_lesson_attachment(self, attachment_id: int, user_id: int) -> bool:
        """Delete lesson attachment"""
        attachment = self.db.query(LessonAttachment).options(
            joinedload(LessonAttachment.lesson).joinedload(Lesson.module).joinedload(Module.course)
        ).filter(LessonAttachment.id == attachment_id).first()
        
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        # Check if user is the course instructor or admin
        if attachment.lesson.module.course.instructor_id != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this attachment"
            )
        
        self.db.delete(attachment)
        self.db.commit()
        
        return True
    
    # Enrollment Methods
    def enroll_user(self, enrollment_create: UserEnrollmentCreate, user_id: int) -> UserEnrollment:
        """Enroll user in a course"""
        # Check if course exists
        course = self.get_course_by_id(enrollment_create.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        if not course.is_published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot enroll in unpublished course"
            )
        
        # Check if user is already enrolled
        existing_enrollment = self.db.query(UserEnrollment).filter(
            and_(
                UserEnrollment.user_id == user_id,
                UserEnrollment.course_id == enrollment_create.course_id
            )
        ).first()
        
        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already enrolled in this course"
            )
        
        # Create enrollment
        db_enrollment = UserEnrollment(
            user_id=user_id,
            course_id=enrollment_create.course_id,
            enrolled_at=datetime.utcnow()
        )
        
        self.db.add(db_enrollment)
        
        # Update course enrollment count
        course.enrollment_count += 1
        
        self.db.commit()
        self.db.refresh(db_enrollment)
        
        return db_enrollment
    
    def get_user_enrollments(self, user_id: int, skip: int = 0, limit: int = 10) -> List[UserEnrollment]:
        """Get user's course enrollments"""
        return self.db.query(UserEnrollment).options(
            joinedload(UserEnrollment.course).joinedload(Course.instructor)
        ).filter(
            UserEnrollment.user_id == user_id
        ).order_by(
            desc(UserEnrollment.enrolled_at)
        ).offset(skip).limit(limit).all()
    
    def get_course_enrollments(self, course_id: int, skip: int = 0, limit: int = 10) -> List[UserEnrollment]:
        """Get course enrollments"""
        return self.db.query(UserEnrollment).options(
            joinedload(UserEnrollment.user)
        ).filter(
            UserEnrollment.course_id == course_id
        ).order_by(
            desc(UserEnrollment.enrolled_at)
        ).offset(skip).limit(limit).all()
    
    def unenroll_user(self, course_id: int, user_id: int) -> bool:
        """Unenroll user from course"""
        enrollment = self.db.query(UserEnrollment).filter(
            and_(
                UserEnrollment.user_id == user_id,
                UserEnrollment.course_id == course_id
            )
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        
        # Update course enrollment count
        course = self.get_course_by_id(course_id)
        if course:
            course.enrollment_count = max(0, course.enrollment_count - 1)
        
        self.db.delete(enrollment)
        self.db.commit()
        
        return True
    
    # Progress Tracking Methods
    def mark_lesson_complete(self, lesson_id: int, user_id: int) -> UserProgress:
        """Mark lesson as completed for user"""
        # Check if lesson exists
        lesson = self.get_lesson_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Check if user is enrolled in the course
        enrollment = self.db.query(UserEnrollment).filter(
            and_(
                UserEnrollment.user_id == user_id,
                UserEnrollment.course_id == lesson.module.course_id
            )
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not enrolled in this course"
            )
        
        # Check if progress already exists
        existing_progress = self.db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.lesson_id == lesson_id
            )
        ).first()
        
        if existing_progress:
            existing_progress.is_completed = True
            existing_progress.completed_at = datetime.utcnow()
            progress = existing_progress
        else:
            progress = UserProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=True,
                completed_at=datetime.utcnow()
            )
            self.db.add(progress)
        
        self.db.commit()
        self.db.refresh(progress)
        
        # Update overall course progress
        self._update_course_progress(user_id, lesson.module.course_id)
        
        return progress
    
    def get_user_course_progress(self, user_id: int, course_id: int) -> Optional[UserProgress]:
        """Get user's progress for a specific course"""
        return self.db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.course_id == course_id
            )
        ).first()
    
    def _update_course_progress(self, user_id: int, course_id: int):
        """Update user's overall progress for a course"""
        # Get total lessons in course
        total_lessons = self.db.query(func.count(Lesson.id)).join(
            Module, Lesson.module_id == Module.id
        ).filter(Module.course_id == course_id).scalar()
        
        # Get completed lessons by user
        completed_lessons = self.db.query(func.count(UserProgress.id)).join(
            Lesson, UserProgress.lesson_id == Lesson.id
        ).join(
            Module, Lesson.module_id == Module.id
        ).filter(
            and_(
                Module.course_id == course_id,
                UserProgress.user_id == user_id,
            UserProgress.is_completed == True
            )
        ).scalar()
        
        # Calculate progress percentage
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Update or create progress record
        existing_progress = self.get_user_course_progress(user_id, course_id)
        
        if existing_progress:
            existing_progress.progress_percentage = progress_percentage
            existing_progress.last_accessed_at = datetime.utcnow()
            if progress_percentage >= 100:
                existing_progress.is_completed = True
                existing_progress.completed_at = datetime.utcnow()
        else:
            progress = UserProgress(
                user_id=user_id,
                course_id=course_id,
                progress_percentage=progress_percentage,
                is_completed=progress_percentage >= 100,
                completed_at=datetime.utcnow() if progress_percentage >= 100 else None,
                last_accessed_at=datetime.utcnow()
            )
            self.db.add(progress)
        
        self.db.commit()