import { ApiError, AuthenticationError } from '../errors';
import type { HttpClient, HttpRequestConfig } from '../http';

interface ErrorLike {
  response?: { status?: number; data?: unknown; statusText?: string };
  message?: string;
}

function describe(body: unknown, fallback: string): string {
  if (typeof body === 'string' && body) {
    return body;
  }
  if (body && typeof body === 'object') {
    try {
      return JSON.stringify(body);
    } catch {
      return fallback;
    }
  }
  return fallback;
}

export function toSdkError(error: unknown): Error {
  const err = error as ErrorLike;
  const status = err?.response?.status ?? null;
  const body = err?.response?.data ?? null;
  const message = describe(body, err?.message ?? 'Request failed');

  if (status === 401 || status === 403) {
    return new AuthenticationError(`HTTP ${status}: ${message}`);
  }
  return new ApiError(status, message, body);
}

export abstract class BaseResource {
  protected readonly http: HttpClient;

  protected readonly baseUrl: string;

  constructor(http: HttpClient, baseUrl: string) {
    this.http = http;
    this.baseUrl = baseUrl;
  }

  protected async getJson<T>(path: string, config?: HttpRequestConfig): Promise<T> {
    return this.send<T>(() => this.http.get<T>(`${this.baseUrl}${path}`, config));
  }

  protected async postJson<T>(path: string, data?: unknown, config?: HttpRequestConfig): Promise<T> {
    return this.send<T>(() => this.http.post<T>(`${this.baseUrl}${path}`, data, config));
  }

  protected async putJson<T>(path: string, data?: unknown, config?: HttpRequestConfig): Promise<T> {
    return this.send<T>(() => this.http.put<T>(`${this.baseUrl}${path}`, data, config));
  }

  protected async patchJson<T>(path: string, data?: unknown, config?: HttpRequestConfig): Promise<T> {
    return this.send<T>(() => this.http.patch<T>(`${this.baseUrl}${path}`, data, config));
  }

  protected async deleteJson<T>(path: string, config?: HttpRequestConfig): Promise<T> {
    return this.send<T>(() => this.http.delete<T>(`${this.baseUrl}${path}`, config));
  }

  private async send<T>(call: () => Promise<{ data: T }>): Promise<T> {
    try {
      const response = await call();
      return response.data;
    } catch (error) {
      throw toSdkError(error);
    }
  }
}
