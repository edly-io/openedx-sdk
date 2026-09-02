import axios from 'axios';

export interface HttpRequestConfig {
  params?: Record<string, unknown>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

export interface HttpResponse<T = unknown> {
  data: T;
  status: number;
}

/**
 * Minimal contract the SDK needs from an HTTP client. An axios instance
 * satisfies it, including the authenticated one from @edx/frontend-platform.
 */
export interface HttpClient {
  get<T = unknown>(url: string, config?: HttpRequestConfig): Promise<HttpResponse<T>>;
  post<T = unknown>(url: string, data?: unknown, config?: HttpRequestConfig): Promise<HttpResponse<T>>;
  put<T = unknown>(url: string, data?: unknown, config?: HttpRequestConfig): Promise<HttpResponse<T>>;
  patch<T = unknown>(url: string, data?: unknown, config?: HttpRequestConfig): Promise<HttpResponse<T>>;
  delete<T = unknown>(url: string, config?: HttpRequestConfig): Promise<HttpResponse<T>>;
}

export function createDefaultHttpClient(timeout = 30000): HttpClient {
  return axios.create({ timeout, withCredentials: true }) as unknown as HttpClient;
}

export function stripTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '');
}

export function joinUrl(base: string, path: string): string {
  return `${stripTrailingSlash(base)}${path}`;
}

/** Drops undefined and null entries so they are never serialized. */
export function compactParams(params: Record<string, unknown>): Record<string, unknown> | undefined {
  const entries = Object.entries(params).filter(([, value]) => value !== undefined && value !== null);
  return entries.length ? Object.fromEntries(entries) : undefined;
}

export function booleanParam(value: boolean | undefined): string | undefined {
  if (value === undefined) {
    return undefined;
  }
  return value ? 'true' : 'false';
}
