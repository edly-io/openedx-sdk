"""Base class for SDK resource classes."""

from ..exceptions import ApiError


class BaseResource:
    """Base class for all SDK resource classes."""

    def __init__(self, session):
        self._session = session

    def _get(self, url, params=None):
        """Make a GET request and return the parsed JSON response."""
        response = self._session.get(url, params=params)
        if not response.ok:
            raise ApiError(response.status_code, response.text)
        return response.json()
