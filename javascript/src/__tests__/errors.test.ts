import { OpenEdxClient } from '../client';
import { ApiError, AuthenticationError, OpenEdxSdkError } from '../errors';
import { toSdkError } from '../resources/base';
import { createFakeHttpClient, httpError } from './helpers';

describe('error mapping', () => {
  it('maps 404 to ApiError carrying status and body', async () => {
    const http = createFakeHttpClient();
    http.get.mockRejectedValue(httpError(404, { detail: 'Not found' }));
    const client = new OpenEdxClient({ studioBase: 'https://studio.example.com', httpClient: http });

    await expect(client.home.v3.courses()).rejects.toBeInstanceOf(ApiError);
    await expect(client.home.v3.courses()).rejects.toMatchObject({
      status: 404,
      body: { detail: 'Not found' },
    });
  });

  it('maps 401 and 403 to AuthenticationError', () => {
    expect(toSdkError(httpError(401))).toBeInstanceOf(AuthenticationError);
    expect(toSdkError(httpError(403))).toBeInstanceOf(AuthenticationError);
  });

  it('maps a network failure with no response to ApiError with null status', () => {
    const error = toSdkError(new Error('Network Error')) as ApiError;
    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBeNull();
    expect(error.message).toContain('Network Error');
  });

  it('keeps ApiError and AuthenticationError under the SDK base error', () => {
    expect(new ApiError(500, 'boom')).toBeInstanceOf(OpenEdxSdkError);
    expect(new AuthenticationError('nope')).toBeInstanceOf(OpenEdxSdkError);
  });

  it('preserves error names for logging', () => {
    expect(new ApiError(500, 'boom').name).toBe('ApiError');
    expect(new AuthenticationError('nope').name).toBe('AuthenticationError');
    expect(new OpenEdxSdkError('base').name).toBe('OpenEdxSdkError');
  });
});
