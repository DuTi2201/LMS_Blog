#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.user import User
from app.core.security import get_password_hash
from datetime import datetime
import uuid

def create_test_users():
    """Create test admin and user accounts"""
    try:
        with Session(engine) as db:
            # Check if admin already exists (by email or username)
            existing_admin = db.query(User).filter(
                (User.email == "vuvanduong802@gmail.com") | (User.username == "admin")
            ).first()
            if existing_admin:
                print("Admin user already exists, skipping...")
            else:
                # Create admin user
                admin_user = User(
                    id=uuid.uuid4(),
                    email="vuvanduong802@gmail.com",
                    username="admin",
                    full_name="Administrator",
                    hashed_password=get_password_hash("admin123"),
                    role="admin",
                    is_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(admin_user)
                print("Admin user created successfully!")
            
            # Check if test user already exists (by email or username)
            existing_user = db.query(User).filter(
                (User.email == "vu69712@gmail.com") | (User.username == "testuser")
            ).first()
            if existing_user:
                print("Test user already exists, skipping...")
            else:
                # Create test user
                test_user = User(
                    id=uuid.uuid4(),
                    email="vu69712@gmail.com",
                    username="testuser",
                    full_name="Test User",
                    hashed_password=get_password_hash("user123"),
                    role="user",
                    is_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(test_user)
                print("Test user created successfully!")
            
            db.commit()
            print("\nTest accounts created successfully!")
            print("\nAdmin Account:")
            print("- Email: vuvanduong802@gmail.com")
            print("- Username: admin")
            print("- Password: admin123")
            print("- Role: admin")
            print("\nUser Account:")
            print("- Email: vu69712@gmail.com")
            print("- Username: testuser")
            print("- Password: user123")
            print("- Role: user")
            
    except Exception as e:
        print(f"Error creating test users: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_test_users()