"""
Exceptions raised by the Open edX SDK.
"""


class OpenEdxSdkError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(OpenEdxSdkError):
    """Raised when JWT acquisition or refresh fails."""


class ApiError(OpenEdxSdkError):
    """Raised when the API returns a non-2xx response."""

    def __init__(self, status_code, message):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")
