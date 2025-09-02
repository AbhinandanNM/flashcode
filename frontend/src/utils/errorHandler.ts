// Error types for different scenarios
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
}

export class AppError extends Error {
  public status?: number;
  public code?: string;
  public details?: any;

  constructor(message: string, status?: number, code?: string, details?: any) {
    super(message);
    this.name = 'AppError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

// User-friendly error messages for common HTTP status codes
const statusMessages: Record<number, string> = {
  400: 'Invalid request. Please check your input and try again.',
  401: 'You need to log in to access this feature.',
  403: 'You don\'t have permission to perform this action.',
  404: 'The requested resource was not found.',
  409: 'This action conflicts with existing data.',
  422: 'The provided data is invalid.',
  429: 'Too many requests. Please wait a moment and try again.',
  500: 'Server error. Please try again later.',
  502: 'Service temporarily unavailable. Please try again later.',
  503: 'Service temporarily unavailable. Please try again later.',
  504: 'Request timeout. Please try again.'
};

// Network error messages
const networkErrorMessages = {
  NETWORK_ERROR: 'Network error. Please check your internet connection.',
  TIMEOUT: 'Request timed out. Please try again.',
  CORS_ERROR: 'Cross-origin request blocked. Please contact support.',
  UNKNOWN: 'An unexpected error occurred. Please try again.'
};

export const handleApiError = (error: any): ApiError => {
  // Handle network errors
  if (!error.response) {
    if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
      return {
        message: networkErrorMessages.NETWORK_ERROR,
        code: 'NETWORK_ERROR'
      };
    }
    
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return {
        message: networkErrorMessages.TIMEOUT,
        code: 'TIMEOUT'
      };
    }
    
    return {
      message: networkErrorMessages.UNKNOWN,
      code: 'UNKNOWN'
    };
  }

  const { status, data } = error.response;
  
  // Handle API errors with custom messages
  if (data?.message) {
    return {
      message: data.message,
      status,
      code: data.code,
      details: data.details
    };
  }
  
  // Handle validation errors
  if (status === 422 && data?.errors) {
    const validationErrors = Object.values(data.errors).flat();
    return {
      message: validationErrors.join(', '),
      status,
      code: 'VALIDATION_ERROR',
      details: data.errors
    };
  }
  
  // Use default status messages
  const message = statusMessages[status] || 'An unexpected error occurred.';
  
  return {
    message,
    status,
    code: `HTTP_${status}`
  };
};

export const getErrorMessage = (error: any): string => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error instanceof AppError) {
    return error.message;
  }
  
  if (error?.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred.';
};

// Specific error handlers for different contexts
export const handleAuthError = (error: any): ApiError => {
  const apiError = handleApiError(error);
  
  // Customize auth-specific messages
  if (apiError.status === 401) {
    return {
      ...apiError,
      message: 'Invalid credentials. Please check your email and password.'
    };
  }
  
  if (apiError.status === 409 && apiError.code === 'USER_EXISTS') {
    return {
      ...apiError,
      message: 'An account with this email already exists.'
    };
  }
  
  return apiError;
};

export const handleLessonError = (error: any): ApiError => {
  const apiError = handleApiError(error);
  
  // Customize lesson-specific messages
  if (apiError.status === 404) {
    return {
      ...apiError,
      message: 'Lesson not found. It may have been removed or you may not have access.'
    };
  }
  
  return apiError;
};

export const handleCodeExecutionError = (error: any): ApiError => {
  const apiError = handleApiError(error);
  
  // Customize code execution messages
  if (apiError.status === 408 || apiError.code === 'TIMEOUT') {
    return {
      ...apiError,
      message: 'Code execution timed out. Please optimize your code and try again.'
    };
  }
  
  if (apiError.status === 400 && apiError.code === 'COMPILATION_ERROR') {
    return {
      ...apiError,
      message: 'Code compilation failed. Please check your syntax.'
    };
  }
  
  return apiError;
};

// Error logging utility
export const logError = (error: any, context?: string) => {
  const errorInfo = {
    message: getErrorMessage(error),
    context,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href,
    stack: error?.stack
  };
  
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error logged:', errorInfo);
  }
  
  // In production, send to error monitoring service
  if (process.env.NODE_ENV === 'production') {
    // TODO: Send to error monitoring service (e.g., Sentry, LogRocket)
    console.error('Production error:', errorInfo);
  }
};

// Retry utility for failed requests
export const withRetry = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: any;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Don't retry on client errors (4xx) except 408, 429
      if (error.response?.status >= 400 && error.response?.status < 500) {
        if (error.response.status !== 408 && error.response.status !== 429) {
          throw error;
        }
      }
      
      // Don't retry on last attempt
      if (attempt === maxRetries) {
        break;
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay * attempt));
    }
  }
  
  throw lastError;
};