from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base


# Association table for many-to-many relationship between BlogPost and BlogTag
blog_post_tags = Table(
    'blog_post_tags',
    Base.metadata,
    Column('post_id', UUID(as_uuid=True), ForeignKey('blog_posts.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('blog_tags.id'), primary_key=True)
)


class BlogCategory(Base):
    __tablename__ = "blog_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), default='#3B82F6', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    blog_posts = relationship("BlogPost", secondary=blog_post_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<BlogTag(id={self.id}, name='{self.name}')>"


class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    status = Column(String(20), default="draft", nullable=False)  # draft, published, archived
    view_count = Column(Integer, default=0, nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    read_time_minutes = Column(Integer, default=0, nullable=False)
    featured_image_url = Column(String(500), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("blog_categories.id"), nullable=True)
    
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