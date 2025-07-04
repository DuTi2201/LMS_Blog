#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from sqlalchemy.orm import Session

def create_test_enrollment():
    """Create enrollment for user@lms.com in Web Development with FastAPI course"""
    db = next(get_db())
    
    try:
        # Find user
        user = db.query(User).filter(User.email == 'user@lms.com').first()
        if not user:
            print("❌ User user@lms.com not found")
            return
        
        # Find course
        course = db.query(Course).filter(Course.title == 'Web Development with FastAPI').first()
        if not course:
            print("❌ Course 'Web Development with FastAPI' not found")
            return
        
        # Check if enrollment already exists
        existing_enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == user.id,
            Enrollment.course_id == course.id
        ).first()
        
        if existing_enrollment:
            print(f"✅ Enrollment already exists for {user.email} in '{course.title}'")
            return
        
        # Create new enrollment
        enrollment = Enrollment(
            user_id=user.id,
            course_id=course.id
        )
        
        db.add(enrollment)
        db.commit()
        
        print(f"✅ Successfully enrolled {user.email} in '{course.title}'")
        print(f"   User ID: {user.id}")
        print(f"   Course ID: {course.id}")
        print(f"   Enrollment ID: {enrollment.id}")
        
    except Exception as e:
        print(f"❌ Error creating enrollment: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_enrollment()