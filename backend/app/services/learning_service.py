from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Tuple, Optional

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
            short_description=None,
            thumbnail_url=course_create.featured_image,
            difficulty_level=course_create.level,
            estimated_duration=course_create.duration_hours,
            is_published=course_create.is_published,
            price=0.0,
            instructor_id=instructor_id
        )
        
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)
        
        return db_course
    
    def get_lessons_by_module(self, module_id: str, skip: int = 0, limit: int = 50) -> List[Lesson]:
        """Get lessons by module ID"""
        return self.db.query(Lesson).filter(
            Lesson.module_id == module_id
        ).order_by(Lesson.order_index).offset(skip).limit(limit).all()
    
    def get_lessons(self, skip: int = 0, limit: int = 50) -> List[Lesson]:
        """Get all lessons"""
        return self.db.query(Lesson).order_by(
            Lesson.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_courses(self, search_params: CourseSearchParams) -> Tuple[List[Course], int]:
        """Get courses with search and pagination"""
        try:
            # Simple approach: get all courses first, then apply filters
            all_courses = self.db.query(Course).all()
            
            # Apply filters in Python for now to avoid SQL issues
            filtered_courses = []
            for course in all_courses:
                # Apply search filter
                if search_params.q:
                    search_term = search_params.q.lower()
                    if (search_term not in course.title.lower() and 
                        search_term not in (course.description or "").lower()):
                        continue
                
                # Apply instructor filter
                if search_params.instructor_id and course.instructor_id != search_params.instructor_id:
                    continue
                
                # Apply difficulty filter
                if search_params.difficulty_level and course.difficulty_level != search_params.difficulty_level:
                    continue
                
                # Apply price filters
                if search_params.min_price is not None and course.price < search_params.min_price:
                    continue
                
                if search_params.max_price is not None and course.price > search_params.max_price:
                    continue
                
                filtered_courses.append(course)
            
            # Apply sorting
            if search_params.sort_by == "title":
                filtered_courses.sort(key=lambda x: x.title, reverse=(search_params.sort_order == "desc"))
            elif search_params.sort_by == "price":
                filtered_courses.sort(key=lambda x: x.price, reverse=(search_params.sort_order == "desc"))
            elif search_params.sort_by == "updated_at":
                filtered_courses.sort(key=lambda x: x.updated_at, reverse=(search_params.sort_order == "desc"))
            else:  # default to created_at
                filtered_courses.sort(key=lambda x: x.created_at, reverse=(search_params.sort_order == "desc"))
            
            # Apply pagination
            total = len(filtered_courses)
            offset = (search_params.page - 1) * search_params.size
            paginated_courses = filtered_courses[offset:offset + search_params.size]
            
            return paginated_courses, total
            
        except Exception as e:
            print(f"Error in get_courses: {e}")
            return [], 0
    
    def get_course_by_id(self, course_id: str) -> Optional[Course]:
        """Get course by ID with full details"""
        return self.db.query(Course).options(
            joinedload(Course.instructor),
            joinedload(Course.modules).joinedload(Module.lessons).joinedload(Lesson.attachments)
        ).filter(Course.id == course_id).first()
    
    def update_course(self, course_id: str, course_update: CourseUpdate, user_id: str) -> Course:
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
    
    def delete_course(self, course_id: str, user_id: str) -> bool:
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
    
    def enroll_user_in_course(self, user_id: str, course_id: str) -> UserEnrollment:
        """Enroll user in course (for admin use) - allows enrollment in unpublished courses"""
        # Check if course exists
        course = self.get_course_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Admin can enroll users in unpublished courses, so skip is_published check
        
        # Check if user is already enrolled
        existing_enrollment = self.db.query(UserEnrollment).filter(
            and_(
                UserEnrollment.user_id == user_id,
                UserEnrollment.course_id == course_id
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
            course_id=course_id,
            enrolled_at=datetime.utcnow()
        )
        
        self.db.add(db_enrollment)
        
        # Update course enrollment count
        course.enrollment_count += 1
        
        self.db.commit()
        self.db.refresh(db_enrollment)
        
        return db_enrollment
    
    def unenroll_user_from_course(self, user_id: str, course_id: str) -> bool:
        """Unenroll user from course (for admin use)"""
        return self.unenroll_user(course_id, user_id)
    
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
    def get_modules(self, course_id: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Module]:
        """Get modules with optional course filter"""
        query = self.db.query(Module).options(
            joinedload(Module.course),
            joinedload(Module.lessons).joinedload(Lesson.attachments)
        )
        
        if course_id:
            query = query.filter(Module.course_id == course_id)
        
        return query.order_by(Module.order_index).offset(skip).limit(limit).all()
    
    def create_module(self, course_id: str, module_create: ModuleCreate) -> Module:
        """Create a new module"""
        # Check if course exists
        course = self.get_course_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Get next order number if not provided
        order_index = module_create.order_index
        if order_index is None:
            max_order = self.db.query(func.max(Module.order_index)).filter(
                Module.course_id == course_id
            ).scalar() or 0
            order_index = max_order + 1
        
        db_module = Module(
            title=module_create.title,
            description=module_create.description,
            order_index=order_index,
            course_id=course_id,
            is_published=module_create.is_published
        )
        
        self.db.add(db_module)
        self.db.commit()
        self.db.refresh(db_module)
        
        return db_module
    
    def get_modules_by_course_id(self, course_id: str, skip: int = 0, limit: int = 50) -> List[Module]:
        """Get modules for a specific course"""
        return self.db.query(Module).options(
            joinedload(Module.lessons).joinedload(Lesson.attachments)
        ).filter(
            Module.course_id == course_id
        ).order_by(
            Module.order_index
        ).offset(skip).limit(limit).all()
    
    def get_module_by_id(self, module_id: UUID) -> Optional[Module]:
        """Get module by ID with lessons"""
        return self.db.query(Module).options(
            joinedload(Module.course),
            joinedload(Module.lessons).joinedload(Lesson.attachments)
        ).filter(Module.id == module_id).first()
    
    def update_module(self, module_id: UUID, module_update: ModuleUpdate, user_id: str) -> Module:
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
    
    def delete_module(self, module_id: UUID, user_id: str) -> bool:
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
    
    def reorder_modules(self, course_id: str, module_orders: List[dict], user_id: str) -> List[Module]:
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
    def create_lesson(self, lesson_create: LessonCreate, module_id: UUID, user_id: str) -> Lesson:
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
        
        # Get next order number if not provided
        order_index = lesson_create.order_index
        if order_index is None:
            max_order = self.db.query(func.max(Lesson.order_index)).filter(
                Lesson.module_id == module_id
            ).scalar() or 0
            order_index = max_order + 1
        
        db_lesson = Lesson(
            title=lesson_create.title,
            description=lesson_create.description,
            instructor=lesson_create.instructor,
            zoom_link=lesson_create.zoom_link,
            quiz_link=lesson_create.quiz_link,
            notification=lesson_create.notification,
            duration=lesson_create.duration,
            video_url=lesson_create.video_url,
            order_index=order_index,
            is_active=True,  # Default to active
            module_id=module_id
        )
        
        self.db.add(db_lesson)
        self.db.commit()
        self.db.refresh(db_lesson)
        
        return db_lesson
    
    def get_lesson_by_id(self, lesson_id: UUID) -> Optional[Lesson]:
        """Get lesson by ID with attachments"""
        return self.db.query(Lesson).options(
            joinedload(Lesson.module).joinedload(Module.course),
            joinedload(Lesson.attachments)
        ).filter(Lesson.id == lesson_id).first()
    
    def get_lessons_by_module(self, module_id: UUID, skip: int = 0, limit: int = 50) -> List[Lesson]:
        """Get lessons by module ID"""
        return self.db.query(Lesson).options(
            joinedload(Lesson.module).joinedload(Module.course),
            joinedload(Lesson.attachments)
        ).filter(
            Lesson.module_id == module_id
        ).order_by(Lesson.order_index).offset(skip).limit(limit).all()
    
    def update_lesson(self, lesson_id: UUID, lesson_update: LessonUpdate, user_id: str) -> Lesson:
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
    
    def delete_lesson(self, lesson_id: UUID, user_id: str) -> bool:
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
    def create_lesson_attachment(self, attachment_create: LessonAttachmentCreate, lesson_id: UUID, user_id: str) -> LessonAttachment:
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
            name=attachment_create.name,
            url=attachment_create.url,
            file_type=attachment_create.file_type,
            file_size=attachment_create.file_size,
            lesson_id=lesson_id
        )
        
        self.db.add(db_attachment)
        self.db.commit()
        self.db.refresh(db_attachment)
        
        return db_attachment
    
    def delete_lesson_attachment(self, attachment_id: UUID, user_id: str) -> bool:
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
    
    def get_lesson_attachment_by_id(self, attachment_id: UUID) -> Optional[LessonAttachment]:
        """Get lesson attachment by ID"""
        return self.db.query(LessonAttachment).options(
            joinedload(LessonAttachment.lesson).joinedload(Lesson.module).joinedload(Module.course)
        ).filter(LessonAttachment.id == attachment_id).first()
    
    def get_lesson_attachments(self, lesson_id: UUID) -> List[LessonAttachment]:
        """Get all attachments for a lesson"""
        return self.db.query(LessonAttachment).filter(
            LessonAttachment.lesson_id == lesson_id
        ).all()
    
    # Enrollment Methods
    def enroll_user(self, enrollment_create: UserEnrollmentCreate, user_id: str) -> UserEnrollment:
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
    
    def get_user_enrollments(self, user_id: str, skip: int = 0, limit: int = 10) -> List[UserEnrollment]:
        """Get user's course enrollments"""
        return self.db.query(UserEnrollment).options(
            joinedload(UserEnrollment.course).joinedload(Course.instructor)
        ).filter(
            UserEnrollment.user_id == user_id
        ).order_by(
            desc(UserEnrollment.enrolled_at)
        ).offset(skip).limit(limit).all()
    
    def get_user_enrollment(self, user_id: str, course_id: str) -> Optional[UserEnrollment]:
        """Get user's enrollment for a specific course"""
        return self.db.query(UserEnrollment).filter(
            and_(
                UserEnrollment.user_id == user_id,
                UserEnrollment.course_id == course_id
            )
        ).first()
    
    def get_course_enrollments(self, course_id: str, skip: int = 0, limit: int = 10) -> List[UserEnrollment]:
        """Get course enrollments"""
        return self.db.query(UserEnrollment).options(
            joinedload(UserEnrollment.user)
        ).filter(
            UserEnrollment.course_id == course_id
        ).order_by(
            desc(UserEnrollment.enrolled_at)
        ).offset(skip).limit(limit).all()
    
    def unenroll_user(self, course_id: str, user_id: str) -> bool:
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
    def mark_lesson_complete(self, lesson_id: UUID, user_id: str) -> UserProgress:
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
    
    def uncomplete_lesson(self, lesson_id: UUID, user_id: str) -> bool:
        """Mark lesson as uncompleted for user"""
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
        
        # Find existing progress
        existing_progress = self.db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.lesson_id == lesson_id
            )
        ).first()
        
        if existing_progress:
            existing_progress.is_completed = False
            existing_progress.completed_at = None
            self.db.commit()
            
            # Update overall course progress
            self._update_course_progress(user_id, lesson.module.course_id)
            
            return True
        
        return False
    
    def get_user_lesson_progress(self, user_id: str, lesson_id: UUID) -> Optional[UserProgress]:
        """Get user's progress for a specific lesson"""
        return self.db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.lesson_id == lesson_id
            )
        ).first()
    
    def get_user_course_progress(self, user_id: str, course_id: str) -> Optional[UserProgress]:
        """Get user's progress for a specific course"""
        return self.db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.course_id == course_id
            )
        ).first()
    
    def _update_course_progress(self, user_id: str, course_id: str):
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