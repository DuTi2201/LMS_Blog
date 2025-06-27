#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.blog import BlogPost, BlogCategory, BlogTag
from app.models.learning import Course, Module, Lesson
from app.core.security import get_password_hash
import uuid
from datetime import datetime

def create_sample_data():
    session = SessionLocal()
    try:
        print("Creating sample data...")
        
        # Create users one by one
        print("Creating users...")
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@lms.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        session.add(admin_user)
        session.commit()
        
        instructor_user = User(
            id=uuid.uuid4(),
            email="instructor@lms.com",
            username="instructor",
            full_name="John Instructor",
            hashed_password=get_password_hash("instructor123"),
            role="instructor",
            is_active=True
        )
        session.add(instructor_user)
        session.commit()
        
        student_user = User(
            id=uuid.uuid4(),
            email="student@lms.com",
            username="student",
            full_name="Jane Student",
            hashed_password=get_password_hash("student123"),
            role="user",
            is_active=True
        )
        session.add(student_user)
        session.commit()
        print("✓ Sample users created")
        
        # Create blog categories
        print("Creating blog categories...")
        tech_category = BlogCategory(
            id=uuid.uuid4(),
            name="Technology",
            description="Technology related posts",
            slug="technology"
        )
        session.add(tech_category)
        session.commit()
        
        education_category = BlogCategory(
            id=uuid.uuid4(),
            name="Education",
            description="Educational content and tutorials",
            slug="education"
        )
        session.add(education_category)
        session.commit()
        print("✓ Blog categories created")
        
        # Create blog tags
        print("Creating blog tags...")
        python_tag = BlogTag(
            id=uuid.uuid4(),
            name="Python",
            color="#3776ab"
        )
        session.add(python_tag)
        session.commit()
        
        fastapi_tag = BlogTag(
            id=uuid.uuid4(),
            name="FastAPI",
            color="#009688"
        )
        session.add(fastapi_tag)
        session.commit()
        
        tutorial_tag = BlogTag(
            id=uuid.uuid4(),
            name="Tutorial",
            color="#ff9800"
        )
        session.add(tutorial_tag)
        session.commit()
        print("✓ Blog tags created")
        
        # Create blog posts
        print("Creating blog posts...")
        blog_post1 = BlogPost(
            id=uuid.uuid4(),
            title="Getting Started with FastAPI",
            content="FastAPI is a modern, fast web framework for building APIs with Python...",
            status="published",
            author_id=instructor_user.id,
            category_id=tech_category.id
        )
        session.add(blog_post1)
        session.commit()
        
        blog_post2 = BlogPost(
            id=uuid.uuid4(),
            title="Python Best Practices",
            content="Learn the best practices for writing clean and maintainable Python code...",
            status="published",
            author_id=admin_user.id,
            category_id=education_category.id
        )
        session.add(blog_post2)
        session.commit()
        print("✓ Blog posts created")
        
        # Create courses
        print("Creating courses...")
        course1 = Course(
            id=uuid.uuid4(),
            title="Complete Python Programming",
            description="Learn Python from basics to advanced concepts",
            short_description="Master Python programming",
            difficulty_level="beginner",
            is_published=True,
            price=99.99,
            estimated_duration=40,
            instructor_id=instructor_user.id
        )
        session.add(course1)
        session.commit()
        
        course2 = Course(
            id=uuid.uuid4(),
            title="Web Development with FastAPI",
            description="Build modern web APIs with FastAPI",
            short_description="FastAPI web development",
            difficulty_level="intermediate",
            is_published=True,
            price=149.99,
            estimated_duration=25,
            instructor_id=instructor_user.id
        )
        session.add(course2)
        session.commit()
        print("✓ Courses created")
        
        # Create modules
        print("Creating modules...")
        module1 = Module(
            id=uuid.uuid4(),
            title="Python Basics",
            description="Introduction to Python programming",
            order_index=1,
            is_published=True,
            course_id=course1.id
        )
        session.add(module1)
        session.commit()
        
        module2 = Module(
            id=uuid.uuid4(),
            title="FastAPI Fundamentals",
            description="Learn the basics of FastAPI",
            order_index=1,
            is_published=True,
            course_id=course2.id
        )
        session.add(module2)
        session.commit()
        print("✓ Modules created")
        
        # Create lessons
        print("Creating lessons...")
        lesson1 = Lesson(
            id=uuid.uuid4(),
            title="Variables and Data Types",
            description="Learn about Python variables and data types",
            instructor_name="John Instructor",
            order_index=1,
            is_active=True,
            module_id=module1.id
        )
        session.add(lesson1)
        session.commit()
        
        lesson2 = Lesson(
            id=uuid.uuid4(),
            title="Creating Your First API",
            description="Build your first API with FastAPI",
            instructor_name="John Instructor",
            order_index=1,
            is_active=True,
            module_id=module2.id
        )
        session.add(lesson2)
        session.commit()
        print("✓ Lessons created")
        
        print("\n🎉 Sample data created successfully!")
        print("\nCreated:")
        print("- 3 users (admin, instructor, student)")
        print("- 2 blog categories")
        print("- 3 blog tags")
        print("- 2 blog posts")
        print("- 2 courses")
        print("- 2 modules")
        print("- 2 lessons")
        
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_sample_data()