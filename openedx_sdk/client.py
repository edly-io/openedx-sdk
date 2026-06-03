"""
Main entry point for the Open edX Python SDK.
"""

from types import SimpleNamespace

import requests

from .auth import JwtAuth
from .resources.home.v4 import HomeResourceV4


class OpenEdxClient:
    """
    Client for the Open edX REST APIs.

    Handles JWT authentication automatically — tokens are acquired on first
    use and refreshed transparently before expiry.

    :param lms_base: Base URL of the LMS, e.g. ``https://lms.example.com``.
    :param client_id: OAuth2 client ID registered in Django OAuth Toolkit.
    :param client_secret: OAuth2 client secret.
    :param studio_base: Base URL of Studio. Defaults to ``lms_base`` if not
                        provided (common in Tutor where LMS and Studio share
                        a host via port or subdomain).
    :param timeout: Default request timeout in seconds. Defaults to 30.

    Resources are grouped by area, then version::

        from openedx_sdk import OpenEdxClient

        client = OpenEdxClient(
            lms_base="https://lms.example.com",
            client_id="my-client-id",
            client_secret="my-client-secret",
            studio_base="https://studio.example.com",
        )

        # v4 — paginated courses (ADR 0032)
        data = client.home.v4.courses(org="edX", page=1, page_size=20)
        for course in data["results"]["courses"]:
            print(course["display_name"], course["is_active"])

    """

    def __init__(self, lms_base, client_id, client_secret, *, studio_base=None, timeout=30):
        self._lms_base = lms_base.rstrip("/")
        self._studio_base = (studio_base or lms_base).rstrip("/")
        self._timeout = timeout

        self._session = requests.Session()
        self._session.auth = JwtAuth(
            lms_base=self._lms_base,
            client_id=client_id,
            client_secret=client_secret,
        )
        # Apply default timeout to all requests via an adapter hook.
        self._session.request = self._request_with_timeout

        self.home = SimpleNamespace(
            v4=HomeResourceV4(self._session, self._studio_base),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _request_with_timeout(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self._timeout)
        return requests.Session.request(self._session, method, url, **kwargs)
