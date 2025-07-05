#!/usr/bin/env python3
import psycopg2
import json
from datetime import datetime

def check_lesson_data():
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            database='lms_db',
            user='vuduong',
            port=5432
        )
        cur = conn.cursor()
        
        # First check table structure
        print("=== LESSONS TABLE STRUCTURE ===")
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'lessons'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        if columns:
            print("Columns in lessons table:")
            for col in columns:
                print(f"  {col[0]} ({col[1]}) - Nullable: {col[2]}")
        else:
            print("No lessons table found")
            return
        
        # Check recent lessons with available fields
        print("\n=== RECENT LESSONS DATA ===")
        cur.execute("""
            SELECT * FROM lessons 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        rows = cur.fetchall()
        
        if not rows:
            print("No lessons found in database")
        else:
            # Get column names for display
            col_names = [desc[0] for desc in cur.description]
            
            for i, row in enumerate(rows, 1):
                print(f"\n--- Lesson {i} ---")
                for j, value in enumerate(row):
                    print(f"{col_names[j]}: {value if value is not None else 'NULL'}")
        
        # Check if there's a separate attachments table
        print("\n=== CHECKING FOR ATTACHMENTS TABLE ===")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%attachment%'
        """)
        
        attachment_tables = cur.fetchall()
        if attachment_tables:
            print("Found attachment-related tables:")
            for table in attachment_tables:
                print(f"  {table[0]}")
                
                # Check structure of attachment table
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, (table[0],))
                
                att_columns = cur.fetchall()
                print(f"    Columns: {[col[0] for col in att_columns]}")
                
                # Check for specific attachment
                search_term = "Documents_2025-5_M01W02 - List_[Slide]-List_V3.pdf"
                cur.execute(f"""
                    SELECT * FROM {table[0]} 
                    WHERE name LIKE %s
                """, (f'%{search_term}%',))
                
                found_attachments = cur.fetchall()
                
                # Also check all attachments in this table
                cur.execute(f"SELECT * FROM {table[0]} ORDER BY uploaded_at DESC LIMIT 10")
                all_attachments = cur.fetchall()
                print(f"    Recent attachments in {table[0]}:")
                for att in all_attachments:
                    print(f"      {att}")
                if found_attachments:
                    print(f"    Found {len(found_attachments)} matching attachments:")
                    for att in found_attachments:
                        print(f"      {att}")
                else:
                    print(f"    No attachments found matching '{search_term}'")
        else:
            print("No attachment tables found")
            
        # Check all tables to understand the schema
        print("\n=== ALL TABLES IN DATABASE ===")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        all_tables = cur.fetchall()
        print("Tables in database:")
        for table in all_tables:
            print(f"  {table[0]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_lesson_data()