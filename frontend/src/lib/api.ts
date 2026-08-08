/**
 * Centralized API configuration for RTLGen AI Frontend.
 *
 * Base URL resolution order:
 * 1. process.env.NEXT_PUBLIC_API_URL (used in Vercel production deployment)
 * 2. process.env.NEXT_PUBLIC_BACKEND_URL (legacy / alternative env variable)
 * 3. http://127.0.0.1:8000 (default for local development)
 */

export const getApiBaseUrl = (): string => {
  const envUrl =
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    "http://127.0.0.1:8000";

  // Strip trailing slashes to ensure consistent URL formatting
  return envUrl.replace(/\/+$/, "");
};

export const API_BASE_URL = getApiBaseUrl();

/**
 * Helper function to construct full API endpoint URLs.
 * @param path Endpoint path, e.g. "/health" or "/api/v1/generate"
 */
export const getApiUrl = (path: string): string => {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
};

export const ENDPOINTS = {
  HEALTH: getApiUrl("/health"),
  HEALTH_DETAILS: getApiUrl("/health/details"),
  VERSION: getApiUrl("/version"),
  GENERATE: getApiUrl("/api/v1/generate"),
  VALIDATE: getApiUrl("/api/v1/validate"),
  COMPILE: getApiUrl("/api/v1/compile"),
  SIMULATE: getApiUrl("/api/v1/simulate"),
  TESTBENCH: getApiUrl("/api/v1/testbench"),
  HISTORY: getApiUrl("/api/v1/history"),
};
