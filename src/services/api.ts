const API_BASE_URL = 'http://localhost:8000/api';

interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(errorData.detail || 'An error occurred');
    }
    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: this.getHeaders()
    });
    return this.handleResponse<T>(response);
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse<T>(response);
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });
    return this.handleResponse<T>(response);
  }
}

const apiClient = new ApiClient(API_BASE_URL);

// Authentication API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    apiClient.post('/auth/login', credentials),
  
  register: (userData: { username: string; email: string; password: string; full_name?: string }) =>
    apiClient.post('/auth/register', userData),
  
  verifyToken: () =>
    apiClient.get('/auth/verify-token'),
  
  getCurrentUser: () =>
    apiClient.get('/auth/me')
};

// Quiz API
export const quizAPI = {
  createQuiz: (quizData: any) =>
    apiClient.post('/quiz/generate-quiz', quizData),
  
  getNextQuestion: (quizId: string) =>
    apiClient.get(`/quiz/quiz/${quizId}/next-question`),
  
  submitAnswer: (quizId: string, answerData: any) =>
    apiClient.post(`/quiz/quiz/${quizId}/submit-answer`, answerData),
  
  getQuizStats: (quizId: string) =>
    apiClient.get(`/quiz/quiz/${quizId}/stats`),
  
  endQuizSession: (quizId: string) =>
    apiClient.delete(`/quiz/quiz/${quizId}/session`),
  
  getTreeStructure: () =>
    apiClient.get('/quiz/questions/tree-structure'),
  
  searchQuestions: (params: any) =>
    apiClient.get(`/quiz/questions/search?${new URLSearchParams(params)}`)
};

// Analytics API
export const analyticsAPI = {
  getUserStats: () =>
    apiClient.get('/analytics/user-stats'),
  
  getPerformanceTrends: () =>
    apiClient.get('/analytics/performance-trends'),
  
  getDifficultyAnalysis: () =>
    apiClient.get('/analytics/difficulty-analysis')
};