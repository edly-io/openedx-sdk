"""
Main entry point for the Open edX Python SDK.
"""

from types import SimpleNamespace

import requests

from .auth import JwtAuth
from .resources import HomeResourceV3, HomeResourceV4


class _TimeoutSession(requests.Session):
    """Session subclass that applies a default timeout to every request."""

    def __init__(self, timeout):
        super().__init__()
        self._timeout = timeout

    def request(self, *args, **kwargs):
        """Set default timeout then delegate to the standard Session."""
        kwargs.setdefault("timeout", self._timeout)
        return super().request(*args, **kwargs)


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

        # v3 — courses (active + archived, no pagination)
        data = client.home.v3.courses(org="edX")
        for course in data["courses"]:
            print(course["display_name"])
    """

    def __init__(self, lms_base, client_id, client_secret, *, studio_base=None, timeout=30):
        self._lms_base = lms_base.rstrip("/")
        self._studio_base = (studio_base or lms_base).rstrip("/")

        self._session = _TimeoutSession(timeout)
        self._session.auth = JwtAuth(
            lms_base=self._lms_base,
            client_id=client_id,
            client_secret=client_secret,
        )

        self.home = SimpleNamespace(
            v3=HomeResourceV3(self._session, self._studio_base),
            v4=HomeResourceV4(self._session, self._studio_base),
        )
