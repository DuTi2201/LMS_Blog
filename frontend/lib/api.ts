const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://192.168.2.101:8001';

// Response interfaces
export interface User {
  id: string;
  email: string;
  full_name: string;
  username?: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  bio?: string;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
  auth_provider?: string;
  google_id?: string;
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
  description?: string;
  short_description?: string;
  thumbnail_url?: string;
  difficulty_level: string;
  estimated_duration?: number;
  is_published: boolean;
  price: number;
  enrollment_count: number;
  created_at: string;
  updated_at: string;
  instructor_id: string;
  instructor?: User;
  modules?: Module[];
}

export interface CourseData {
  title: string;
  description: string;
  featured_image?: string;
  is_published?: boolean;
  level?: string;
  duration_hours?: number;
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
    options: RequestInit = {},
    retryOnAuth: boolean = true
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    if (!headers['Content-Type'] && options.body) {
        headers['Content-Type'] = 'application/json';
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    let response: Response;
    try {
      response = await fetch(url, {
        ...options,
        headers,
        // Add timeout and better error handling
        signal: AbortSignal.timeout(30000), // 30 second timeout
        // Add cache busting to prevent browser cache issues
        cache: 'no-cache',
        mode: 'cors',
      });
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout. Please check your connection and try again.');
        }
        if (error.message.includes('Failed to fetch')) {
          throw new Error('Network error. Please check your connection and try again.');
        }
      }
      throw error;
    }

    // Handle authentication errors
    if ((response.status === 401 || response.status === 403) && retryOnAuth) {
      // Token might be expired, try to refresh or clear it
      if (typeof window !== 'undefined') {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          try {
            await this.refreshAccessToken();
            // Retry the request with new token
            return this.request<T>(endpoint, options, false);
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            this.clearTokens();
            throw new Error('Session expired. Please login again.');
          }
        } else {
          // No refresh token, clear access token
          this.clearTokens();
          throw new Error('Authentication required. Please login.');
        }
      }
    }

    // For public endpoints (retryOnAuth = false), skip auth error handling
    if (!response.ok && !((response.status === 401 || response.status === 403) && !retryOnAuth)) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    // For public endpoints with auth errors, try to get data anyway
    if ((response.status === 401 || response.status === 403) && !retryOnAuth) {
      // Clear any invalid tokens
      this.clearTokens();
      // Try to parse response anyway, some endpoints might return data
      try {
        return response.json();
      } catch {
        throw new Error('Unable to access this resource. Please try again later.');
      }
    }

    return response.json();
  }

  private clearTokens() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  private async refreshAccessToken() {
    if (typeof window === 'undefined') {
      throw new Error('Cannot refresh token on server side');
    }

    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${this.baseURL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Failed to refresh token');
    }

    const data = await response.json();
    this.token = data.access_token;
    localStorage.setItem('access_token', data.access_token);
    
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token);
    }

    return data;
  }

  // Auth methods
  async login(email: string, password: string): Promise<User> {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const tokenResponse = await this.request<{ access_token: string, refresh_token: string }>(
      '/api/v1/auth/login',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      },
      false // Don't retry on auth error for login
    );

    this.token = tokenResponse.access_token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokenResponse.access_token);
      if (tokenResponse.refresh_token) {
        localStorage.setItem('refresh_token', tokenResponse.refresh_token);
      }
    }

    // After successful login, get user data
    return this.getCurrentUser();
  }

  async googleLogin(googleToken: string): Promise<User> {
    const tokenResponse = await this.request<{ access_token: string, refresh_token: string }>(
      '/api/v1/auth/google-login',
      {
        method: 'POST',
        body: JSON.stringify({ token: googleToken }),
      },
      false // Don't retry on auth error for login
    );

    this.token = tokenResponse.access_token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokenResponse.access_token);
      if (tokenResponse.refresh_token) {
        localStorage.setItem('refresh_token', tokenResponse.refresh_token);
      }
    }

    // After successful login, get user data
    return this.getCurrentUser();
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
    this.clearTokens();
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/v1/auth/me');
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  getToken(): string | null {
    return this.token;
  }

  // Blog methods
  async getBlogPosts(skip: number = 0, limit: number = 10): Promise<BlogPost[]> {
    return this.request<BlogPost[]>(`/api/v1/blogs/?skip=${skip}&limit=${limit}`, {}, false);
  }

  async getBlogPost(id: string): Promise<BlogPost> {
    return this.request<BlogPost>(`/api/v1/blogs/${id}`, {}, false);
  }

  async createBlogPost(data: BlogPostData): Promise<BlogPost> {
    return this.request<BlogPost>('/api/v1/blogs/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateBlogPost(id: string, data: BlogPostData): Promise<BlogPost> {
    return this.request<BlogPost>(`/api/v1/blogs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteBlogPost(id: string): Promise<void> {
    return this.request<void>(`/api/v1/blogs/${id}`, {
      method: 'DELETE',
    });
  }

  async getBlogCategories(): Promise<Category[]> {
    return this.request<Category[]>('/api/v1/blog-categories/', {}, false);
  }

  async getBlogTags(): Promise<Tag[]> {
    return this.request<Tag[]>('/api/v1/blog-tags/', {}, false);
  }

  async createBlogTag(tagData: { name: string }): Promise<Tag> {
    return this.request<Tag>('/api/v1/blog-tags/', {
      method: 'POST',
      body: JSON.stringify(tagData)
    });
  }

  // Learning methods
  async getCourses(skip: number = 0, limit: number = 10): Promise<Course[]> {
    return this.request<Course[]>(`/api/v1/courses/?skip=${skip}&limit=${limit}`, {}, false);
  }

  async getEnrolledCourses(skip: number = 0, limit: number = 10): Promise<Course[]> {
    return this.request<Course[]>(`/api/v1/courses/enrolled?skip=${skip}&limit=${limit}`);
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

  async updateCourse(id: string, courseData: CourseData): Promise<Course> {
    return this.request<Course>(`/api/v1/courses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(courseData),
    });
  }

  async deleteCourse(id: string): Promise<void> {
    return this.request<void>(`/api/v1/courses/${id}`, {
      method: 'DELETE',
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
    const response = await this.request<{items: Lesson[], total: number}>(`/api/v1/modules/${moduleId}/lessons/`);
    return response.items;
  }

  async createLesson(moduleId: string, lessonData: LessonData): Promise<Lesson> {
    return this.request<Lesson>(`/api/v1/modules/${moduleId}/lessons/`, {
      method: 'POST',
      body: JSON.stringify(lessonData),
    });
  }

  // User management methods
  async getUsers(skip: number = 0, limit: number = 100): Promise<User[]> {
    return this.request<User[]>(`/api/v1/users/?skip=${skip}&limit=${limit}`);
  }

  async getUser(id: string): Promise<User> {
    return this.request<User>(`/api/v1/users/${id}`);
  }

  async createUser(userData: {
    email: string;
    full_name: string;
    role?: string;
    course_ids?: string[];
  }): Promise<User> {
    return this.request<User>('/api/v1/auth/admin/create-user', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async updateUser(id: string, userData: {
    email?: string;
    full_name?: string;
    role?: string;
  }): Promise<User> {
    return this.request<User>(`/api/v1/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async deleteUser(id: string): Promise<void> {
    return this.request<void>(`/api/v1/users/${id}`, {
      method: 'DELETE',
    });
  }

  async changeUserRole(id: string, role: string): Promise<User> {
    return this.request<User>(`/api/v1/users/${id}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role }),
    });
  }

  // Enrollment methods
  async getUserEnrollments(userId: string): Promise<any[]> {
    return this.request<any[]>(`/api/v1/users/${userId}/enrollments`);
  }

  async enrollUserInCourse(userId: string, courseId: string): Promise<any> {
    return this.request<any>('/api/v1/enrollments/', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, course_id: courseId }),
    });
  }

  async unenrollUserFromCourse(userId: string, courseId: string): Promise<void> {
    return this.request<void>(`/api/v1/enrollments/${userId}/${courseId}`, {
      method: 'DELETE',
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