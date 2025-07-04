#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from datetime import datetime

def reset_admin_password():
    """Reset admin password and verify it works"""
    try:
        with Session(engine) as db:
            # Find admin user
            admin_user = db.query(User).filter(
                (User.email == "vuvanduong802@gmail.com") | (User.username == "admin")
            ).first()
            
            if not admin_user:
                print("Admin user not found!")
                return
            
            print(f"Found admin user: {admin_user.username} ({admin_user.email})")
            print(f"Current active status: {admin_user.is_active}")
            print(f"Current verified status: {admin_user.is_verified}")
            
            # Reset password
            new_password = "admin123"
            admin_user.hashed_password = get_password_hash(new_password)
            admin_user.is_active = True
            admin_user.is_verified = True
            admin_user.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(admin_user)
            
            # Verify password works
            if verify_password(new_password, admin_user.hashed_password):
                print("✅ Password reset successful and verified!")
                print(f"✅ Admin credentials:")
                print(f"   - Email: {admin_user.email}")
                print(f"   - Username: {admin_user.username}")
                print(f"   - Password: {new_password}")
                print(f"   - Active: {admin_user.is_active}")
                print(f"   - Verified: {admin_user.is_verified}")
            else:
                print("❌ Password verification failed!")
                
    except Exception as e:
        print(f"Error resetting admin password: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_admin_password()