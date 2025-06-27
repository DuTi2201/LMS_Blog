const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Response interfaces
export interface User {
  id: string;
  email: string;
  full_name: string;
  username: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BlogPost {
  id: string;
  title: string;
  content: string;
  excerpt?: string;
  is_published: boolean;
  created_at: string;
  updated_at: string;
  author_id: string;
  category_id?: string;
  word_count?: number;
  author?: User;
  category?: {
    id: string;
    name: string;
    description?: string;
  };
  tags: {
    id: string;
    name: string;
  }[];
}

export interface BlogPostData {
  title: string;
  content: string;
  excerpt?: string;
  category_id?: string;
  tag_ids?: string[];
  is_published?: boolean;
}

export interface Course {
  id: string;
  title: string;
  description: string;
  short_description?: string;
  thumbnail_url?: string;
  difficulty_level: string;
  estimated_duration: number;
  is_published: boolean;
  price: number;
  created_at: string;
  updated_at: string;
  instructor_id: string;
  instructor?: User;
  modules?: Module[];
}

export interface CourseData {
  title: string;
  description: string;
  short_description?: string;
  thumbnail_url?: string;
  difficulty_level?: string;
  estimated_duration?: number;
  is_published?: boolean;
  price?: number;
}

export interface Module {
  id: string;
  title: string;
  description: string;
  order_index: number;
  created_at: string;
  updated_at: string;
  course_id: string;
  lessons?: Lesson[];
}

export interface ModuleData {
  title: string;
  description: string;
  order_index: number;
}

export interface Lesson {
  id: string;
  title: string;
  content: string;
  order_index: number;
  lesson_type: string;
  video_url?: string;
  duration?: number;
  created_at: string;
  updated_at: string;
  module_id: string;
}

export interface LessonData {
  title: string;
  content: string;
  order_index: number;
  lesson_type?: string;
  video_url?: string;
  duration?: number;
}

export interface Category {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
    // Get token from localStorage if available
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth methods
  async login(email: string, password: string) {
    const response = await this.request<{ access_token: string; token_type: string; user: User }>(
      '/api/v1/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ username: email, password }),
      }
    );
    
    this.token = response.access_token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', response.access_token);
    }
    
    return response;
  }

  async register(email: string, password: string, full_name: string, username?: string) {
    // Generate username from email if not provided
    const finalUsername = username || email.split('@')[0];
    
    return this.request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email,
        username: finalUsername,
        full_name,
        password
      }),
    });
  }

  async logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
    this.token = null;
  }

  async getCurrentUser() {
    return this.request('/api/v1/auth/me');
  }

  // Blog methods
  async getBlogPosts(skip: number = 0, limit: number = 10): Promise<BlogPost[]> {
    return this.request<BlogPost[]>(`/api/v1/blogs/?skip=${skip}&limit=${limit}`);
  }

  async getBlogPost(id: string): Promise<BlogPost> {
    return this.request<BlogPost>(`/api/v1/blogs/${id}/`);
  }

  async createBlogPost(data: BlogPostData): Promise<BlogPost> {
    return this.request<BlogPost>('/api/v1/blogs/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateBlogPost(id: string, data: BlogPostData): Promise<BlogPost> {
    return this.request<BlogPost>(`/api/v1/blogs/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteBlogPost(id: string): Promise<void> {
    return this.request<void>(`/api/v1/blogs/${id}/`, {
      method: 'DELETE',
    });
  }

  async getBlogCategories(): Promise<Category[]> {
    return this.request<Category[]>('/api/v1/blog-categories/');
  }

  async getBlogTags(): Promise<Tag[]> {
    return this.request<Tag[]>('/api/v1/blog-tags/');
  }

  async createBlogTag(tagData: { name: string }): Promise<Tag> {
    return this.request<Tag>('/api/v1/blog-tags/', {
      method: 'POST',
      body: JSON.stringify(tagData)
    });
  }

  // Learning methods
  async getCourses(skip: number = 0, limit: number = 10): Promise<Course[]> {
    return this.request<Course[]>(`/api/v1/courses/?skip=${skip}&limit=${limit}`);
  }

  async getCourse(id: string): Promise<Course> {
    return this.request<Course>(`/api/v1/courses/${id}/`);
  }

  async createCourse(courseData: CourseData): Promise<Course> {
    return this.request<Course>('/api/v1/courses/', {
      method: 'POST',
      body: JSON.stringify(courseData),
    });
  }

  async getModules(courseId: string): Promise<Module[]> {
    return this.request<Module[]>(`/api/v1/courses/${courseId}/modules/`);
  }

  async createModule(courseId: string, moduleData: ModuleData): Promise<Module> {
    return this.request<Module>(`/api/v1/courses/${courseId}/modules/`, {
      method: 'POST',
      body: JSON.stringify(moduleData),
    });
  }

  async getLessons(moduleId: string): Promise<Lesson[]> {
    return this.request<Lesson[]>(`/api/v1/modules/${moduleId}/lessons/`);
  }

  async createLesson(moduleId: string, lessonData: LessonData): Promise<Lesson> {
    return this.request<Lesson>(`/api/v1/modules/${moduleId}/lessons/`, {
      method: 'POST',
      body: JSON.stringify(lessonData),
    });
  }

  // File upload
  async uploadFile(file: File, type: 'image' | 'attachment' = 'attachment') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', type);

    const headers: HeadersInit = {};
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseURL}/api/v1/files/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
export default apiClient;