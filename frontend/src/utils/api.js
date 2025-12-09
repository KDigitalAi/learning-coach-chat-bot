// API utility to handle dynamic API endpoints
// Uses environment variable in production, localhost in development

const getApiUrl = () => {
  // Priority 1: Use explicit VITE_API_URL if set (for separate backend deployment)
  // This should be set in Vercel environment variables if backend is on different domain
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Priority 2: In production without VITE_API_URL, use relative paths (same domain)
  // This works when backend is deployed on the same Vercel project
  // Priority 3: In development, use localhost
  return import.meta.env.PROD ? '' : 'http://localhost:8000';
};

export const API_BASE_URL = getApiUrl();

export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };
  
  return fetch(url, { ...defaultOptions, ...options });
};

