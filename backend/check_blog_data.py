#!/usr/bin/env python3
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.blog import BlogPost
from sqlalchemy.orm import sessionmaker
from app.core.database import engine

def check_blog_data():
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        posts = db.query(BlogPost).all()
        print(f'Total blog posts: {len(posts)}')
        
        for i, post in enumerate(posts[:5]):
            print(f'Post {i+1}: {post.title}, Published: {post.is_published}, ID: {post.id}')
            
        # Check published posts specifically
        published_posts = db.query(BlogPost).filter(BlogPost.is_published == True).all()
        print(f'\nPublished posts: {len(published_posts)}')
        
    except Exception as e:
        print(f'Error: {e}')
    finally:
        db.close()

if __name__ == '__main__':
    check_blog_data()