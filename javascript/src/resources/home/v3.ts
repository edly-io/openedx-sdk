import { booleanParam, compactParams, joinUrl } from '../../http';
import type { HttpClient } from '../../http';
import type {
  HomeContextV3Response,
  HomeCoursesV3Response,
  HomeLibrariesParams,
  HomeLibrariesV3Response,
  HomeV3Params,
} from '../../types';
import { BaseResource } from '../base';

const BASE_PATH = '/api/contentstore/v3/home';

/** Studio home endpoints served by HomeViewSet (v3). */
export class HomeResourceV3 extends BaseResource {
  constructor(http: HttpClient, studioBase: string) {
    super(http, joinUrl(studioBase, BASE_PATH));
  }

  /** GET /api/contentstore/v3/home/ */
  get(params: HomeV3Params = {}): Promise<HomeContextV3Response> {
    return this.getJson<HomeContextV3Response>('/', {
      params: compactParams({ org: params.org }),
    });
  }

  /** GET /api/contentstore/v3/home/courses/ */
  courses(params: HomeV3Params = {}): Promise<HomeCoursesV3Response> {
    return this.getJson<HomeCoursesV3Response>('/courses/', {
      params: compactParams({ org: params.org }),
    });
  }

  /** GET /api/contentstore/v3/home/libraries/ */
  libraries(params: HomeLibrariesParams = {}): Promise<HomeLibrariesV3Response> {
    return this.getJson<HomeLibrariesV3Response>('/libraries/', {
      params: compactParams({
        org: params.org,
        is_migrated: booleanParam(params.isMigrated),
      }),
    });
  }
}
