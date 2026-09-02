import { createDefaultHttpClient, stripTrailingSlash } from './http';
import type { HttpClient } from './http';
import { OpenEdxSdkError } from './errors';
import { HomeResourceV3 } from './resources/home/v3';
import { HomeResourceV4 } from './resources/home/v4';

export interface OpenEdxClientOptions {
  /** LMS base URL, for example https://lms.example.com */
  lmsBase?: string;
  /** Studio base URL. Falls back to lmsBase when omitted. */
  studioBase?: string;
  /**
   * HTTP client used for every request. Pass getAuthenticatedHttpClient()
   * from @edx/frontend-platform inside an MFE so the SDK reuses the existing
   * session. Defaults to a plain axios instance.
   */
  httpClient?: HttpClient;
  /** Timeout in ms for the default client. Ignored when httpClient is given. */
  timeout?: number;
}

export interface HomeNamespace {
  v3: HomeResourceV3;
  v4: HomeResourceV4;
}

export class OpenEdxClient {
  readonly lmsBase: string;

  readonly studioBase: string;

  readonly home: HomeNamespace;

  private readonly httpClient: HttpClient;

  constructor(options: OpenEdxClientOptions = {}) {
    const { lmsBase, studioBase, httpClient, timeout = 30000 } = options;

    if (!lmsBase && !studioBase) {
      throw new OpenEdxSdkError('Either lmsBase or studioBase must be provided.');
    }

    this.lmsBase = stripTrailingSlash(lmsBase ?? studioBase ?? '');
    this.studioBase = stripTrailingSlash(studioBase ?? lmsBase ?? '');
    this.httpClient = httpClient ?? createDefaultHttpClient(timeout);

    this.home = {
      v3: new HomeResourceV3(this.httpClient, this.studioBase),
      v4: new HomeResourceV4(this.httpClient, this.studioBase),
    };
  }
}
