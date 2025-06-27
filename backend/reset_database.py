#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from sqlalchemy import text
from app.core.database import engine
from app.models import user, blog, learning
from app.core.database import Base

def reset_database():
    """Drop all tables and recreate them"""
    try:
        # Connect to database
        with engine.connect() as conn:
            # Drop all tables by dropping and recreating the public schema
            print("Dropping all tables...")
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
            conn.execute(text("CREATE SCHEMA public;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
            conn.commit()
            print("All tables dropped successfully!")
        
        # Recreate all tables from models
        print("Creating new tables from models...")
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully!")
        
        print("\nDatabase reset completed successfully!")
        
    except Exception as e:
        print(f"Error resetting database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()