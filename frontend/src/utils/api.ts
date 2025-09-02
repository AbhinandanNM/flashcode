// API utility functions for making authenticated requests
import { handleApiError, logError, withRetry } from './errorHandler';

const API_BASE_URL = 'http://localhost:8000';

export class ApiClient {
  private static getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  private static async handleResponse(response: Response): Promise<any> {
    if (!response.ok) {
      const error = {
        response: {
          status: response.status,
          data: await response.json().catch(() => ({ message: response.statusText }))
        }
      };
      
      // Handle auth errors
      if (response.status === 401) {
        localStorage.removeItem('token');
        window.dispatchEvent(new Event('auth-error'));
      }
      
      const apiError = handleApiError(error);
      logError(apiError, `API ${response.url}`);
      throw apiError;
    }
    
    return response.json().catch(() => null);
  }

  private static async makeRequest(
    endpoint: string, 
    options: RequestInit,
    retryable: boolean = true
  ): Promise<any> {
    const requestFn = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
          ...options,
          headers: {
            ...this.getAuthHeaders(),
            ...options.headers,
          },
        });
        
        return this.handleResponse(response);
      } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          throw {
            message: 'Network error. Please check your internet connection.',
            code: 'NETWORK_ERROR'
          };
        }
        throw error;
      }
    };

    if (retryable) {
      return withRetry(requestFn, 2, 1000);
    }
    
    return requestFn();
  }

  static async get(endpoint: string, retryable: boolean = true): Promise<any> {
    return this.makeRequest(endpoint, { method: 'GET' }, retryable);
  }

  static async post(endpoint: string, data?: any, retryable: boolean = false): Promise<any> {
    return this.makeRequest(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }, retryable);
  }

  static async put(endpoint: string, data?: any, retryable: boolean = false): Promise<any> {
    return this.makeRequest(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }, retryable);
  }

  static async delete(endpoint: string, retryable: boolean = false): Promise<any> {
    return this.makeRequest(endpoint, { method: 'DELETE' }, retryable);
  }
}

export default ApiClient;