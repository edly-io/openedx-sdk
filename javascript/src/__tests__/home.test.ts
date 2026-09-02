import { OpenEdxClient } from '../client';
import { createFakeHttpClient } from './helpers';

const STUDIO = 'https://studio.example.com';

function clientWith(data: unknown) {
  const http = createFakeHttpClient(data);
  return { http, client: new OpenEdxClient({ studioBase: STUDIO, httpClient: http }) };
}

describe('HomeResourceV3', () => {
  it('gets the aggregated home context', async () => {
    const payload = { courses: [], archived_courses: [], libraries: [], studio_name: 'Studio' };
    const { http, client } = clientWith(payload);

    const result = await client.home.v3.get();

    expect(http.get).toHaveBeenCalledWith(`${STUDIO}/api/contentstore/v3/home/`, { params: undefined });
    expect(result).toEqual(payload);
  });

  it('passes org when filtering the home context', async () => {
    const { http, client } = clientWith({});
    await client.home.v3.get({ org: 'edX' });
    expect(http.get).toHaveBeenCalledWith(`${STUDIO}/api/contentstore/v3/home/`, { params: { org: 'edX' } });
  });

  it('gets courses', async () => {
    const payload = { courses: [], archived_courses: [], in_process_course_actions: [] };
    const { http, client } = clientWith(payload);

    const result = await client.home.v3.courses({ org: 'edX' });

    expect(http.get).toHaveBeenCalledWith(`${STUDIO}/api/contentstore/v3/home/courses/`, {
      params: { org: 'edX' },
    });
    expect(result).toEqual(payload);
  });

  it('gets libraries and serializes isMigrated', async () => {
    const { http, client } = clientWith({ libraries: [] });

    await client.home.v3.libraries({ isMigrated: true });
    expect(http.get).toHaveBeenCalledWith(`${STUDIO}/api/contentstore/v3/home/libraries/`, {
      params: { is_migrated: 'true' },
    });

    await client.home.v3.libraries({ isMigrated: false });
    expect(http.get).toHaveBeenLastCalledWith(`${STUDIO}/api/contentstore/v3/home/libraries/`, {
      params: { is_migrated: 'false' },
    });
  });

  it('omits isMigrated when not supplied', async () => {
    const { http, client } = clientWith({ libraries: [] });
    await client.home.v3.libraries();
    expect(http.get).toHaveBeenCalledWith(`${STUDIO}/api/contentstore/v3/home/libraries/`, {
      params: undefined,
    });
  });
});

describe('HomeResourceV4', () => {
  it('gets paginated courses with no params by default', async () => {
    const { http, client } = clientWith({ count: 0, results: { courses: [] } });
    await client.home.v4.courses();
    expect(http.get).toHaveBeenCalledWith(`${STUDIO}/api/contentstore/v4/home/courses/`, {
      params: undefined,
    });
  });

  it('maps camelCase options to snake_case query params', async () => {
    const { http, client } = clientWith({ count: 0, results: { courses: [] } });

    await client.home.v4.courses({
      org: 'edX',
      search: 'intro',
      ordering: '-display_name',
      activeOnly: true,
      archivedOnly: false,
      page: 2,
      pageSize: 20,
    });

    expect(http.get).toHaveBeenCalledWith(`${STUDIO}/api/contentstore/v4/home/courses/`, {
      params: {
        org: 'edX',
        search: 'intro',
        ordering: '-display_name',
        active_only: 'true',
        archived_only: 'false',
        page: 2,
        page_size: 20,
      },
    });
  });

  it('returns the paginated envelope', async () => {
    const payload = {
      count: 1,
      num_pages: 1,
      current_page: 1,
      start: 0,
      next: null,
      previous: null,
      results: { courses: [{ course_key: 'course-v1:edX+X+1', is_active: true }], in_process_course_actions: [] },
    };
    const { client } = clientWith(payload);

    const result = await client.home.v4.courses({ page: 1 });

    expect(result.count).toBe(1);
    expect(result.results.courses[0]?.course_key).toBe('course-v1:edX+X+1');
  });
});
