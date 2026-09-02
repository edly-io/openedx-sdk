import { OpenEdxClient } from '../client';
import { OpenEdxSdkError } from '../errors';
import { createFakeHttpClient } from './helpers';

describe('OpenEdxClient', () => {
  it('throws when no base url is provided', () => {
    expect(() => new OpenEdxClient({})).toThrow(OpenEdxSdkError);
  });

  it('defaults studioBase to lmsBase', () => {
    const client = new OpenEdxClient({ lmsBase: 'https://lms.example.com' });
    expect(client.studioBase).toBe('https://lms.example.com');
  });

  it('keeps studioBase and lmsBase separate when both are given', () => {
    const client = new OpenEdxClient({
      lmsBase: 'https://lms.example.com',
      studioBase: 'https://studio.example.com',
    });
    expect(client.lmsBase).toBe('https://lms.example.com');
    expect(client.studioBase).toBe('https://studio.example.com');
  });

  it('strips trailing slashes from base urls', () => {
    const client = new OpenEdxClient({
      lmsBase: 'https://lms.example.com/',
      studioBase: 'https://studio.example.com///',
    });
    expect(client.lmsBase).toBe('https://lms.example.com');
    expect(client.studioBase).toBe('https://studio.example.com');
  });

  it('exposes the home resources', () => {
    const client = new OpenEdxClient({ studioBase: 'https://studio.example.com' });
    expect(client.home.v3).toBeDefined();
    expect(client.home.v4).toBeDefined();
  });

  it('routes requests through the injected http client', async () => {
    const http = createFakeHttpClient({ courses: [] });
    const client = new OpenEdxClient({ studioBase: 'https://studio.example.com', httpClient: http });
    await client.home.v3.courses();
    expect(http.get).toHaveBeenCalledTimes(1);
  });
});
