#!/usr/bin/env python3
"""
Script to create test accounts for LMS system
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_path = str(Path(__file__).parent / "app")
sys.path.insert(0, app_path)

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy import select

def create_test_accounts():
    """Create test accounts for different roles"""
    
    # Test accounts data
    test_accounts = [
        {
            "email": "admin@lms.com",
            "username": "admin",
            "full_name": "System Administrator",
            "password": "admin123",
            "role": "admin",
            "is_active": True
        },
        {
            "email": "user@lms.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "user123",
            "role": "user",
            "is_active": True
        },
        {
            "email": "instructor@lms.com",
            "username": "instructor",
            "full_name": "Test Instructor",
            "password": "instructor123",
            "role": "instructor",
            "is_active": True
        }
    ]
    
    session = SessionLocal()
    try:
        for account_data in test_accounts:
            # Check if user already exists
            result = session.execute(
                select(User).where(User.email == account_data["email"])
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"User {account_data['email']} already exists, skipping...")
                continue
            
            # Create new user
            hashed_password = get_password_hash(account_data["password"])
            
            new_user = User(
                email=account_data["email"],
                username=account_data["username"],
                full_name=account_data["full_name"],
                hashed_password=hashed_password,
                role=account_data["role"],
                is_active=account_data["is_active"]
            )
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            print(f"✅ Created {account_data['role']} account:")
            print(f"   Email: {account_data['email']}")
            print(f"   Username: {account_data['username']}")
            print(f"   Password: {account_data['password']}")
            print(f"   Role: {account_data['role']}")
            print(f"   User ID: {new_user.id}")
            print()
            
    except Exception as e:
        print(f"❌ Error creating test accounts: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("Creating test accounts for LMS system...")
    print("=" * 50)
    
    try:
        create_test_accounts()
        print("✅ Test accounts created successfully!")
        print("\nYou can now use these accounts to test the system:")
        print("- Admin: admin@lms.com / admin123")
        print("- User: user@lms.com / user123")
        print("- Instructor: instructor@lms.com / instructor123")
    except Exception as e:
        print(f"❌ Failed to create test accounts: {e}")
        sys.exit(1)