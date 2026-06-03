"""
JWT authentication handler for the Open edX SDK.

Handles token acquisition via OAuth2 client_credentials grant and automatic
refresh using grant_type=refresh_token before the token expires.
"""

import time

import requests

from .exceptions import AuthenticationError

_EXPIRY_BUFFER_SECONDS = 300  # refresh when < 5 minutes remain


class JwtAuth(requests.auth.AuthBase):
    """
    Requests auth handler that injects a valid JWT into every request.

    Transparently acquires and refreshes tokens so callers never manage
    tokens manually.

    Usage::

        auth = JwtAuth(
            lms_base="https://lms.example.com",
            client_id="my-client-id",
            client_secret="my-client-secret",
        )
        session = requests.Session()
        session.auth = auth
        response = session.get(
            "https://studio.example.com/api/contentstore/v4/home/courses/"
        )
    """

    TOKEN_PATH = "/oauth2/access_token/"

    def __init__(self, lms_base, client_id, client_secret):
        self._token_url = lms_base.rstrip("/") + self.TOKEN_PATH
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = None
        self._refresh_token = None
        self._expires_at = 0

    # ------------------------------------------------------------------
    # requests.auth.AuthBase interface
    # ------------------------------------------------------------------

    def __call__(self, r):
        """Attach the JWT Authorization header to the request."""
        r.headers["Authorization"] = f"JWT {self._get_token()}"
        return r

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_token(self):
        """Get a valid access token, refreshing or re-acquiring as needed."""
        if self._access_token and self._expires_at - time.time() > _EXPIRY_BUFFER_SECONDS:
            return self._access_token
        if self._refresh_token:
            self._refresh()
        else:
            self._authenticate()
        return self._access_token

    def _authenticate(self):
        """Acquire a new token via client_credentials grant."""
        response = requests.post(
            self._token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "token_type": "jwt",
            },
            timeout=10,
        )
        self._handle_token_response(response)

    def _refresh(self):
        """Refresh the access token using the stored refresh token."""
        response = requests.post(
            self._token_url,
            data={
                "grant_type": "refresh_token",
                "client_id": self._client_id,
                "refresh_token": self._refresh_token,
                "token_type": "jwt",
            },
            timeout=10,
        )
        if response.status_code == 400:
            # Refresh token expired — fall back to full re-authentication.
            self._refresh_token = None
            self._authenticate()
            return
        self._handle_token_response(response)

    def _handle_token_response(self, response):
        """Parse a token endpoint response and store credentials."""
        if not response.ok:
            raise AuthenticationError(
                f"Failed to obtain access token: HTTP {response.status_code} — {response.text}"
            )
        data = response.json()
        self._access_token = data["access_token"]
        self._refresh_token = data.get("refresh_token")
        # expires_in is in seconds; fall back to 3600 (1 hour) if absent.
        self._expires_at = time.time() + data.get("expires_in", 3600)
