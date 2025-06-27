from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


# Association table for many-to-many relationship between BlogPost and BlogTag
blog_post_tags = Table(
    'blog_post_tags',
    Base.metadata,
    Column('blog_post_id', Integer, ForeignKey('blog_posts.id'), primary_key=True),
    Column('blog_tag_id', Integer, ForeignKey('blog_tags.id'), primary_key=True)
)


class BlogCategory(Base):
    __tablename__ = "blog_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    blog_posts = relationship("BlogPost", back_populates="category")
    
    def __repr__(self):
        return f"<BlogCategory(id={self.id}, name='{self.name}')>"


class BlogTag(Base):
    __tablename__ = "blog_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    blog_posts = relationship("BlogPost", secondary=blog_post_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<BlogTag(id={self.id}, name='{self.name}')>"


class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    slug = Column(String(255), unique=True, nullable=False)
    featured_image = Column(String(500), nullable=True)
    status = Column(String(20), default="draft", nullable=False)  # draft, published, archived
    is_featured = Column(Boolean, default=False, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    reading_time = Column(Integer, nullable=True)  # in minutes
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("blog_categories.id"), nullable=True)
    
    # Relationships
    author = relationship("User", back_populates="blog_posts")
    category = relationship("BlogCategory", back_populates="blog_posts")
    tags = relationship("BlogTag", secondary=blog_post_tags, back_populates="blog_posts")
    
    def __repr__(self):
        return f"<BlogPost(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def is_published(self) -> bool:
        return self.status == "published"


# For backward compatibility, create an alias
BlogPostTag = blog_post_tags