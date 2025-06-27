#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.blog import BlogPost, BlogCategory, BlogTag
from app.models.learning import Course, Module, Lesson, LessonAttachment, UserEnrollment

def clear_all_data():
    session = SessionLocal()
    try:
        print("Clearing all data...")
        
        # Delete in reverse order of dependencies
        session.query(LessonAttachment).delete()
        session.query(Lesson).delete()
        session.query(Module).delete()
        session.query(UserEnrollment).delete()
        session.query(Course).delete()
        session.query(BlogPost).delete()
        session.query(BlogTag).delete()
        session.query(BlogCategory).delete()
        session.query(User).delete()
        
        session.commit()
        print("✓ All data cleared successfully")
        
    except Exception as e:
        print(f"✗ Error clearing data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    clear_all_data()