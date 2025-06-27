          
# Tài Liệu Thiết Kế Hệ Thống Backend FastAPI và Database PostgreSQL

## Tổng Quan Hệ Thống

Dựa trên phân tích frontend Next.js hiện tại, hệ thống backend cần hỗ trợ 3 module chính:
- **Learning Management System (LMS)** - Quản lý khóa học, module, bài học
- **Blog Management System** - Quản lý bài viết blog với rich content
- **Authentication & Authorization** - Xác thực và phân quyền người dùng

---

## 1. Kiến Trúc Hệ Thống

### 1.1 Tech Stack
- **Backend Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT + OAuth2
- **File Storage**: AWS S3 / Local Storage
- **Cache**: Redis (optional)
- **API Documentation**: Swagger UI (tự động từ FastAPI)

### 1.2 Cấu Trúc Project
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── blog.py
│   │   └── learning.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── blog.py
│   │   └── learning.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── blogs.py
│   │       └── learning.py
│   └── services/
│       ├── __init__.py
│       ├── auth_service.py
│       ├── blog_service.py
│       └── learning_service.py
├── alembic/
├── requirements.txt
└── docker-compose.yml
```

---

## 2. Database Schema Design

### 2.1 Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user', -- 'admin', 'user', 'guest'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 Blog System Tables
```sql
-- Blog Categories
CREATE TABLE blog_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blog Posts
CREATE TABLE blog_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    author_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES blog_categories(id),
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'published', 'archived'
    word_count INTEGER DEFAULT 0,
    read_time_minutes INTEGER DEFAULT 0,
    featured_image_url VARCHAR(500),
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blog Tags
CREATE TABLE blog_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#3B82F6'
);

-- Blog Post Tags (Many-to-Many)
CREATE TABLE blog_post_tags (
    post_id UUID REFERENCES blog_posts(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES blog_tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);
```

### 2.3 Learning Management System Tables
```sql
-- Courses
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    instructor_id UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Modules
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lessons
CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    lesson_date DATE,
    instructor_name VARCHAR(255),
    zoom_link VARCHAR(500),
    quiz_link VARCHAR(500),
    notification TEXT,
    order_index INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lesson Attachments
CREATE TABLE lesson_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Course Enrollments
CREATE TABLE user_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    UNIQUE(user_id, course_id)
);
```

---

## 3. API Endpoints Design

### 3.1 Authentication Endpoints
```python
# /api/v1/auth
POST   /auth/login          # Đăng nhập
POST   /auth/register       # Đăng ký
POST   /auth/refresh        # Refresh token
POST   /auth/logout         # Đăng xuất
GET    /auth/me             # Thông tin user hiện tại
```

### 3.2 Blog Management Endpoints
```python
# /api/v1/blogs
GET    /blogs               # Lấy danh sách blog (public + pagination)
GET    /blogs/{id}          # Lấy chi tiết blog
POST   /blogs               # Tạo blog mới (auth required)
PUT    /blogs/{id}          # Cập nhật blog (auth + owner/admin)
DELETE /blogs/{id}          # Xóa blog (auth + owner/admin)
GET    /blogs/search        # Tìm kiếm blog

# /api/v1/blog-categories
GET    /blog-categories     # Lấy danh sách categories
POST   /blog-categories     # Tạo category (admin only)
PUT    /blog-categories/{id} # Cập nhật category (admin only)
DELETE /blog-categories/{id} # Xóa category (admin only)

# /api/v1/blog-tags
GET    /blog-tags           # Lấy danh sách tags
POST   /blog-tags           # Tạo tag mới
```

### 3.3 Learning Management Endpoints
```python
# /api/v1/courses
GET    /courses             # Lấy danh sách khóa học
GET    /courses/{id}        # Lấy chi tiết khóa học
POST   /courses             # Tạo khóa học (admin only)
PUT    /courses/{id}        # Cập nhật khóa học (admin only)
DELETE /courses/{id}        # Xóa khóa học (admin only)

# /api/v1/modules
GET    /courses/{course_id}/modules    # Lấy modules của course
POST   /courses/{course_id}/modules    # Tạo module (admin only)
PUT    /modules/{id}                   # Cập nhật module (admin only)
DELETE /modules/{id}                  # Xóa module (admin only)

# /api/v1/lessons
GET    /modules/{module_id}/lessons    # Lấy lessons của module
POST   /modules/{module_id}/lessons    # Tạo lesson (admin only)
PUT    /lessons/{id}                   # Cập nhật lesson (admin only)
DELETE /lessons/{id}                  # Xóa lesson (admin only)

# /api/v1/attachments
POST   /lessons/{lesson_id}/attachments # Upload file attachment
DELETE /attachments/{id}              # Xóa attachment
```

---

## 4. Models & Schemas

### 4.1 Pydantic Schemas (Request/Response)
```python
# schemas/blog.py
class BlogPostCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[UUID] = None
    tag_ids: List[UUID] = []
    status: str = "draft"
    featured_image_url: Optional[str] = None

class BlogPostResponse(BaseModel):
    id: UUID
    title: str
    content: str
    excerpt: Optional[str]
    author: UserResponse
    category: Optional[CategoryResponse]
    tags: List[TagResponse]
    status: str
    word_count: int
    read_time_minutes: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

# schemas/learning.py
class LessonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    lesson_date: Optional[date] = None
    instructor_name: Optional[str] = None
    zoom_link: Optional[str] = None
    quiz_link: Optional[str] = None
    notification: Optional[str] = None
    order_index: int

class LessonResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    lesson_date: Optional[date]
    instructor_name: Optional[str]
    zoom_link: Optional[str]
    quiz_link: Optional[str]
    notification: Optional[str]
    attachments: List[AttachmentResponse]
    order_index: int
    created_at: datetime
```

### 4.2 SQLAlchemy Models
```python
# models/blog.py
class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    category_id = Column(UUID(as_uuid=True), ForeignKey("blog_categories.id"))
    status = Column(String(20), default="draft")
    word_count = Column(Integer, default=0)
    read_time_minutes = Column(Integer, default=0)
    featured_image_url = Column(String(500))
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship("User", back_populates="blog_posts")
    category = relationship("BlogCategory")
    tags = relationship("BlogTag", secondary="blog_post_tags")
```

---

## 5. Security & Authentication

### 5.1 JWT Configuration
```python
# core/security.py
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 5.2 Role-Based Access Control
```python
# api/deps.py
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_auth(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user
```

---

## 6. File Upload & Storage

### 6.1 File Upload Service
```python
# services/file_service.py
class FileService:
    def __init__(self):
        self.upload_dir = "uploads/"
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".jpg", ".png"}
    
    async def upload_file(self, file: UploadFile, folder: str = "general") -> str:
        # Validate file
        if file.size > self.max_file_size:
            raise HTTPException(400, "File too large")
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        if file_extension not in self.allowed_extensions:
            raise HTTPException(400, "File type not allowed")
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = Path(self.upload_dir) / folder / unique_filename
        
        # Save file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(file_path)
```

---

## 7. Deployment & Configuration

### 7.1 Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/lms_db
      - SECRET_KEY=your-secret-key
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=lms_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 7.2 Environment Configuration
```python
# core/config.py
class Settings(BaseSettings):
    PROJECT_NAME: str = "LMS Backend API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 8. Testing Strategy

### 8.1 Unit Tests
```python
# tests/test_blog_api.py
def test_create_blog_post(client, admin_token):
    response = client.post(
        "/api/v1/blogs",
        json={
            "title": "Test Blog",
            "content": "Test content",
            "status": "published"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Blog"
```

### 8.2 Integration Tests
```python
# tests/test_learning_flow.py
def test_complete_learning_flow(client, admin_token, user_token):
    # Admin creates course
    course_response = client.post("/api/v1/courses", ...)
    
    # Admin creates module
    module_response = client.post(f"/api/v1/courses/{course_id}/modules", ...)
    
    # User enrolls in course
    enrollment_response = client.post(f"/api/v1/courses/{course_id}/enroll", ...)
    
    # User views lessons
    lessons_response = client.get(f"/api/v1/modules/{module_id}/lessons", ...)
```

---

## 9. Performance & Optimization

### 9.1 Database Indexing
```sql
-- Performance indexes
CREATE INDEX idx_blog_posts_status ON blog_posts(status);
CREATE INDEX idx_blog_posts_author ON blog_posts(author_id);
CREATE INDEX idx_blog_posts_published ON blog_posts(published_at DESC);
CREATE INDEX idx_lessons_module ON lessons(module_id, order_index);
CREATE INDEX idx_modules_course ON modules(course_id, order_index);
```

### 9.2 Caching Strategy
```python
# services/cache_service.py
class CacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour
    
    async def get_blog_posts(self, page: int, limit: int):
        cache_key = f"blog_posts:{page}:{limit}"
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_blog_posts(self, page: int, limit: int, data: dict):
        cache_key = f"blog_posts:{page}:{limit}"
        await self.redis.setex(cache_key, self.default_ttl, json.dumps(data))
```

---

## 10. Monitoring & Logging

### 10.1 Logging Configuration
```python
# core/logging.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
```

### 10.2 Health Check Endpoint
```python
# api/v1/health.py
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": settings.VERSION
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {str(e)}")
```

Hệ thống backend này được thiết kế để hỗ trợ đầy đủ các chức năng của frontend hiện tại, với khả năng mở rộng và bảo mật cao, phù hợp cho việc phát triển một LMS hoàn chỉnh.
        ##  Admin Account
- Email: admin@lms.com
- Username: admin
- Password: admin123
- Role: admin
- Quyền: Quản trị viên có quyền truy cập đầy đủ
## 👤 User Account
- Email: user@lms.com
- Username: testuser
- Password: user123
- Role: user
- Quyền: Người dùng thông thường

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000