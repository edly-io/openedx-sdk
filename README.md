# openedx-sdk

Client SDKs for the standardized Open edX REST APIs.

This repository holds one SDK per language. Each package is self contained and
versioned independently.

| Directory | Package | Description |
| --- | --- | --- |
| [`python/`](./python) | `openedx-sdk` (PyPI) | Python SDK, for server to server use. Authenticates with an OAuth2 client credentials grant and manages JWTs itself. |
| [`javascript/`](./javascript) | `@openedx/openedx-sdk` (npm) | JavaScript/TypeScript SDK, aimed at MFEs. Reuses the caller's authenticated HTTP client instead of handling credentials. |

Both SDKs expose the same resource shape, grouped by area and then version:

```
client.home.v3.courses()
client.home.v4.courses(...)
```

## Covered APIs

| Area | Version | Endpoint |
| --- | --- | --- |
| Studio home | v3 | `GET /api/contentstore/v3/home/` |
| Studio home | v3 | `GET /api/contentstore/v3/home/courses/` |
| Studio home | v3 | `GET /api/contentstore/v3/home/libraries/` |
| Studio home | v4 | `GET /api/contentstore/v4/home/courses/` |

## Getting started

- Python: see [`python/README.rst`](./python/README.rst)
- JavaScript: see [`javascript/README.md`](./javascript/README.md)

## License

AGPL 3.0. See [LICENSE.txt](./LICENSE.txt).
