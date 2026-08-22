import { OpenAPI } from './generated';

// Configure generated OpenAPI client base URL from environment
OpenAPI.BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
OpenAPI.WITH_CREDENTIALS = true;

// Re-export generated services and models
export * from './generated';
