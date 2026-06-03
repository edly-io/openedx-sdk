"""
Python SDK for Open edX REST APIs.
"""

__version__ = '0.1.0'

from .client import OpenEdxClient
from .exceptions import ApiError, AuthenticationError, OpenEdxSdkError

__all__ = [
    "OpenEdxClient",
    "ApiError",
    "AuthenticationError",
    "OpenEdxSdkError",
]
