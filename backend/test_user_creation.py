#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
import uuid

def test_user_creation():
    session = SessionLocal()
    try:
        # Test creating a single user
        test_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password=get_password_hash("password123"),
            role="user",
            is_active=True
        )
        
        session.add(test_user)
        session.commit()
        print("✓ Test user created successfully")
        
        # Query the user back
        created_user = session.query(User).filter(User.email == "test@example.com").first()
        if created_user:
            print(f"✓ User found: {created_user.username} - {created_user.email}")
        else:
            print("✗ User not found after creation")
            
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    test_user_creation()