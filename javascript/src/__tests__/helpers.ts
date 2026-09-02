import type { HttpClient, HttpResponse } from '../http';

export interface FakeHttpClient extends HttpClient {
  get: jest.Mock;
  post: jest.Mock;
  put: jest.Mock;
  patch: jest.Mock;
  delete: jest.Mock;
}

export function createFakeHttpClient(data: unknown = {}, status = 200): FakeHttpClient {
  const response: HttpResponse = { data, status };
  return {
    get: jest.fn().mockResolvedValue(response),
    post: jest.fn().mockResolvedValue(response),
    put: jest.fn().mockResolvedValue(response),
    patch: jest.fn().mockResolvedValue(response),
    delete: jest.fn().mockResolvedValue(response),
  } as unknown as FakeHttpClient;
}

export function httpError(status: number, data: unknown = 'boom') {
  return Object.assign(new Error(`Request failed with status code ${status}`), {
    response: { status, data },
  });
}
