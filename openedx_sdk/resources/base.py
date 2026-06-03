"""Base class for SDK resource classes."""

import requests

from ..exceptions import ApiError


class BaseResource:
    """Base class for all SDK resource classes."""

    def __init__(self, session):
        self._session = session

    def _get(self, url, params=None):
        """Make a GET request and return the parsed JSON response."""
        try:
            response = self._session.get(url, params=params)
        except requests.RequestException as exc:
            raise ApiError(None, str(exc)) from exc
        if not response.ok:
            raise ApiError(response.status_code, response.text)
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(response.status_code, "Invalid JSON response") from exc
