#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine, text
from core.config import settings

def check_lessons():
    """Check if there are any lessons with 'demo' in the title"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check for lessons with 'demo' in title
            result = conn.execute(
                text("SELECT id, title, description, module_id, order_index, created_at FROM lessons WHERE title ILIKE '%demo%'")
            )
            lessons = result.fetchall()
            
            print(f"Found {len(lessons)} lessons with 'demo' in title:")
            for lesson in lessons:
                print(f"  ID: {lesson[0]}")
                print(f"  Title: {lesson[1]}")
                print(f"  Description: {lesson[2]}")
                print(f"  Module ID: {lesson[3]}")
                print(f"  Order Index: {lesson[4]}")
                print(f"  Created At: {lesson[5]}")
                print("  ---")
            
            # Also check total number of lessons
            total_result = conn.execute(text("SELECT COUNT(*) FROM lessons"))
            total_count = total_result.fetchone()[0]
            print(f"\nTotal lessons in database: {total_count}")
            
            # Check recent lessons (last 10)
            recent_result = conn.execute(
                text("SELECT id, title, module_id, created_at FROM lessons ORDER BY created_at DESC LIMIT 10")
            )
            recent_lessons = recent_result.fetchall()
            
            print(f"\nRecent lessons (last 10):")
            for lesson in recent_lessons:
                print(f"  {lesson[1]} (ID: {lesson[0]}, Module: {lesson[2]}, Created: {lesson[3]})")
                
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_lessons()