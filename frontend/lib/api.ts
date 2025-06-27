const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

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
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
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
    const response = await this.request<{ access_token: string; token_type: string; user: any }>(
      '/api/v1/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }
    );
    
    this.token = response.access_token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', response.access_token);
    }
    
    return response;
  }

  async register(userData: { email: string; password: string; full_name: string }) {
    return this.request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
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
  async getBlogPosts(skip: number = 0, limit: number = 10) {
    return this.request(`/api/v1/blogs?skip=${skip}&limit=${limit}`);
  }

  async getBlogPost(id: number) {
    return this.request(`/api/v1/blogs/${id}`);
  }

  async createBlogPost(postData: any) {
    return this.request('/api/v1/blogs', {
      method: 'POST',
      body: JSON.stringify(postData),
    });
  }

  async updateBlogPost(id: number, postData: any) {
    return this.request(`/api/v1/blogs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(postData),
    });
  }

  async deleteBlogPost(id: number) {
    return this.request(`/api/v1/blogs/${id}`, {
      method: 'DELETE',
    });
  }

  async getBlogCategories() {
    return this.request('/api/v1/blog-categories');
  }

  async getBlogTags() {
    return this.request('/api/v1/blog-tags');
  }

  // Learning methods
  async getCourses(skip: number = 0, limit: number = 10) {
    return this.request(`/api/v1/courses?skip=${skip}&limit=${limit}`);
  }

  async getCourse(id: number) {
    return this.request(`/api/v1/courses/${id}`);
  }

  async createCourse(courseData: any) {
    return this.request('/api/v1/courses', {
      method: 'POST',
      body: JSON.stringify(courseData),
    });
  }

  async getModules(courseId: number) {
    return this.request(`/api/v1/courses/${courseId}/modules`);
  }

  async createModule(courseId: number, moduleData: any) {
    return this.request(`/api/v1/courses/${courseId}/modules`, {
      method: 'POST',
      body: JSON.stringify(moduleData),
    });
  }

  async getLessons(moduleId: number) {
    return this.request(`/api/v1/modules/${moduleId}/lessons`);
  }

  async createLesson(moduleId: number, lessonData: any) {
    return this.request(`/api/v1/modules/${moduleId}/lessons`, {
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