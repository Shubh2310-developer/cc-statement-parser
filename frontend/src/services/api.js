/**
 * API Client Configuration
 *
 * Centralized Axios instance with interceptors for request/response handling.
 * Provides:
 * - Base URL configuration from environment
 * - Default headers and timeout settings
 * - Request/response logging (dev mode)
 * - Global error handling and normalization
 * - Automatic retry logic for transient failures
 * - Token injection for authenticated routes
 */

import axios from 'axios';

/**
 * Environment configuration
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 30000; // 30 seconds
const IS_DEV = import.meta.env.DEV;

/**
 * Create Axios instance with default configuration
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  // Enable credentials for CORS if needed
  withCredentials: false,
});

/**
 * Request Interceptor
 * - Logs outgoing requests in development
 * - Injects authentication token if available
 * - Adds request timestamp for debugging
 */
api.interceptors.request.use(
  (config) => {
    // Inject auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request timestamp for latency tracking
    config.metadata = { startTime: Date.now() };

    // Log requests in development
    if (IS_DEV) {
      console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      });
    }

    return config;
  },
  (error) => {
    if (IS_DEV) {
      console.error('[API Request Error]', error);
    }
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * - Logs responses in development
 * - Normalizes error responses
 * - Handles common HTTP errors (401, 403, 500, etc.)
 */
api.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const duration = Date.now() - response.config.metadata.startTime;

    // Log successful responses in development
    if (IS_DEV) {
      console.log(
        `[API Response] ${response.config.method.toUpperCase()} ${response.config.url} (${duration}ms)`,
        response.data
      );
    }

    return response;
  },
  async (error) => {
    // Extract error details
    const originalRequest = error.config;
    const status = error.response?.status;
    const errorData = error.response?.data;

    // Log errors in development
    if (IS_DEV) {
      console.error('[API Response Error]', {
        url: originalRequest?.url,
        status,
        message: errorData?.message || error.message,
        data: errorData,
      });
    }

    /**
     * Handle specific HTTP status codes
     */
    switch (status) {
      case 401:
        // Unauthorized - clear auth and redirect to login
        localStorage.removeItem('auth_token');
        // Optionally trigger a global event or redirect
        // window.location.href = '/login';
        break;

      case 403:
        // Forbidden - user doesn't have permission
        break;

      case 404:
        // Not found
        break;

      case 429:
        // Too many requests - implement retry with backoff
        if (!originalRequest._retry) {
          originalRequest._retry = true;
          await delay(2000); // Wait 2 seconds before retry
          return api(originalRequest);
        }
        break;

      case 500:
      case 502:
      case 503:
      case 504:
        // Server errors - implement retry logic
        if (!originalRequest._retryCount) {
          originalRequest._retryCount = 0;
        }

        if (originalRequest._retryCount < 3) {
          originalRequest._retryCount++;
          const backoffDelay = Math.pow(2, originalRequest._retryCount) * 1000;
          await delay(backoffDelay);
          return api(originalRequest);
        }
        break;
    }

    /**
     * Normalize error response format
     */
    const normalizedError = {
      message: errorData?.message || error.message || 'An unexpected error occurred',
      status,
      code: errorData?.code,
      details: errorData?.details,
      timestamp: new Date().toISOString(),
    };

    // Attach normalized error to the error object
    error.normalizedError = normalizedError;

    return Promise.reject(error);
  }
);

/**
 * Utility: Delay helper for retry logic
 */
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Utility: Retry wrapper for transient failures
 * Wraps any API call with automatic retry logic
 *
 * @param {Function} apiCall - The API function to execute
 * @param {number} maxRetries - Maximum number of retry attempts (default: 3)
 * @param {number} baseDelay - Base delay in ms for exponential backoff (default: 1000)
 * @returns {Promise} - Result of the API call
 */
export const withRetry = async (apiCall, maxRetries = 3, baseDelay = 1000) => {
  let lastError;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error;

      // Don't retry on client errors (4xx except 429)
      const status = error.response?.status;
      if (status && status >= 400 && status < 500 && status !== 429) {
        throw error;
      }

      // If this was the last attempt, throw the error
      if (attempt === maxRetries) {
        throw error;
      }

      // Calculate exponential backoff delay
      const delayMs = baseDelay * Math.pow(2, attempt);

      if (IS_DEV) {
        console.log(`[API Retry] Attempt ${attempt + 1}/${maxRetries} failed. Retrying in ${delayMs}ms...`);
      }

      await delay(delayMs);
    }
  }

  throw lastError;
};

/**
 * Utility: Check if error is a network error
 */
export const isNetworkError = (error) => {
  return !error.response && error.message === 'Network Error';
};

/**
 * Utility: Check if error is a timeout error
 */
export const isTimeoutError = (error) => {
  return error.code === 'ECONNABORTED' || error.message.includes('timeout');
};

/**
 * Utility: Extract error message from various error formats
 */
export const getErrorMessage = (error) => {
  return (
    error.normalizedError?.message ||
    error.response?.data?.message ||
    error.message ||
    'An unexpected error occurred'
  );
};

/**
 * Export configured API instance
 */
export default api;
