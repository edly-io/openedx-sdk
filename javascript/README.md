# openedx-sdk (JavaScript)

JavaScript/TypeScript client for the standardized Open edX REST APIs.
Built for use inside Micro-frontends (MFEs), and usable from any Node or
browser code that can supply an HTTP client.

## Install

```bash
npm install @openedx/openedx-sdk axios
```

`axios` is a peer dependency. MFEs already have it via `@edx/frontend-platform`.

## Usage in an MFE

Pass the authenticated client from `@edx/frontend-platform` so the SDK reuses
the existing session (JWT cookie, CSRF, refresh). The SDK never handles
credentials itself.

```ts
import { OpenEdxClient } from '@openedx/openedx-sdk';
import { getAuthenticatedHttpClient } from '@edx/frontend-platform/auth';
import { getConfig } from '@edx/frontend-platform';

const client = new OpenEdxClient({
  lmsBase: getConfig().LMS_BASE_URL,
  studioBase: getConfig().STUDIO_BASE_URL,
  httpClient: getAuthenticatedHttpClient(),
});

const page = await client.home.v4.courses({ org: 'edX', page: 1, pageSize: 20 });
page.results.courses.forEach((course) => {
  console.log(course.display_name, course.is_active);
});
```

## Standalone usage

Omit `httpClient` to get a plain axios instance with `withCredentials` enabled.

```ts
const client = new OpenEdxClient({ studioBase: 'https://studio.example.com' });
const home = await client.home.v3.get();
```

## API

Resources are grouped by area, then version, matching the Python SDK.

| Method | Endpoint |
| --- | --- |
| `client.home.v3.get({ org })` | `GET /api/contentstore/v3/home/` |
| `client.home.v3.courses({ org })` | `GET /api/contentstore/v3/home/courses/` |
| `client.home.v3.libraries({ org, isMigrated })` | `GET /api/contentstore/v3/home/libraries/` |
| `client.home.v4.courses({ org, search, ordering, activeOnly, archivedOnly, page, pageSize })` | `GET /api/contentstore/v4/home/courses/` |

Options are camelCase and are mapped to the snake_case query params the API
expects. Responses are returned as the API sends them, so response fields stay
snake_case and match the backend contract.

`home.v4.courses` returns the ADR 0032 pagination envelope:

```ts
{
  count, num_pages, current_page, start, next, previous,
  results: { courses: [...], in_process_course_actions: [...] }
}
```

## Errors

All failures throw a subclass of `OpenEdxSdkError`.

- `AuthenticationError` for 401 and 403
- `ApiError` for any other non-2xx response, and for network failures where
  `status` is `null`

```ts
import { ApiError, AuthenticationError } from '@openedx/openedx-sdk';

try {
  await client.home.v4.courses();
} catch (error) {
  if (error instanceof AuthenticationError) {
    // redirect to login
  } else if (error instanceof ApiError) {
    console.error(error.status, error.body);
  }
}
```

## Development

```bash
npm install
npm run validate      # lint, typecheck and test
npm run build         # dual CJS/ESM build with type declarations
```

## Adding a resource

1. Add response types to `src/types.ts`.
2. Add a resource class under `src/resources/<area>/<version>.ts` extending
   `BaseResource`, using `getJson`, `postJson`, `putJson`, `patchJson` or
   `deleteJson`.
3. Register it on the client in `src/client.ts` and export it from
   `src/resources/index.ts`.
