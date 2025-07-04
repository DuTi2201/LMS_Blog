#!/usr/bin/env python3
import sys
sys.path.append('/Users/vuduong/Desktop/LMS_Prj/backend')

from app.core.database import get_db
from app.models.learning import Course

def main():
    db = next(get_db())
    try:
        courses = db.query(Course).all()
        print("Available courses:")
        for course in courses:
            print(f"ID: {course.id}, Title: {course.title}")
        
        if courses:
            print(f"\nFirst course ID for testing: {courses[0].id}")
        else:
            print("\nNo courses found in database")
    finally:
        db.close()

if __name__ == "__main__":
    main()