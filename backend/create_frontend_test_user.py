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

def create_frontend_test_user():
    """Create test user for frontend testing"""
    try:
        with Session(engine) as db:
            # Create test user with email that frontend might use
            test_email = "testuser@lms.com"
            existing_user = db.query(User).filter(
                (User.email == test_email) | (User.username == "testuser")
            ).first()
            
            if existing_user:
                print(f"Test user already exists: {existing_user.email}")
                # Update password to ensure it's correct
                existing_user.hashed_password = get_password_hash("user123")
                existing_user.is_active = True
                existing_user.is_verified = True
                existing_user.updated_at = datetime.utcnow()
                db.commit()
                print("✅ Test user password updated!")
            else:
                # Create new test user
                test_user = User(
                    id=uuid.uuid4(),
                    email=test_email,
                    username="testuser",
                    full_name="Test User",
                    hashed_password=get_password_hash("user123"),
                    role="user",
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(test_user)
                db.commit()
                print("✅ Test user created successfully!")
            
            print(f"\n📋 Frontend Test Credentials:")
            print(f"   - Email: {test_email}")
            print(f"   - Username: testuser")
            print(f"   - Password: user123")
            print(f"   - Role: user")
            
    except Exception as e:
        print(f"Error creating frontend test user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_frontend_test_user()