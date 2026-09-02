import { booleanParam, compactParams, joinUrl } from '../../http';
import type { HttpClient } from '../../http';
import type { HomeCoursesV4Params, HomeCoursesV4Response } from '../../types';
import { BaseResource } from '../base';

const BASE_PATH = '/api/contentstore/v4/home/courses';

/** Studio home courses endpoint served by HomeCoursesViewSet (v4). */
export class HomeResourceV4 extends BaseResource {
  constructor(http: HttpClient, studioBase: string) {
    super(http, joinUrl(studioBase, BASE_PATH));
  }

  /** GET /api/contentstore/v4/home/courses/ with pagination, filtering and ordering. */
  courses(params: HomeCoursesV4Params = {}): Promise<HomeCoursesV4Response> {
    return this.getJson<HomeCoursesV4Response>('/', {
      params: compactParams({
        org: params.org,
        search: params.search,
        ordering: params.ordering,
        active_only: booleanParam(params.activeOnly),
        archived_only: booleanParam(params.archivedOnly),
        page: params.page,
        page_size: params.pageSize,
      }),
    });
  }
}
