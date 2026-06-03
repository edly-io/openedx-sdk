"""
Tests for the Open edX SDK.
"""

import time

import pytest
import responses as rsps
from responses import matchers

from openedx_sdk import ApiError, AuthenticationError, OpenEdxClient
from openedx_sdk.auth import JwtAuth

LMS_BASE = "http://lms.example.com"
STUDIO_BASE = "http://studio.example.com"
CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-client-secret"
TOKEN_URL = f"{LMS_BASE}/oauth2/access_token/"

FAKE_TOKEN = "header.eyJleHAiOiA5OTk5OTk5OTk5fQ.sig"  # exp: 9999999999 (year 2286)
FAKE_REFRESH_TOKEN = "fake-refresh-token"

# ---------------------------------------------------------------------------
# URL constants
# ---------------------------------------------------------------------------

V3_HOME_URL = f"{STUDIO_BASE}/api/contentstore/v3/home/"
V3_COURSES_URL = f"{STUDIO_BASE}/api/contentstore/v3/home/courses/"
V3_LIBRARIES_URL = f"{STUDIO_BASE}/api/contentstore/v3/home/libraries/"
V4_COURSES_URL = f"{STUDIO_BASE}/api/contentstore/v4/home/courses/"

# ---------------------------------------------------------------------------
# Response factories
# ---------------------------------------------------------------------------


def _token_response(
    access_token=FAKE_TOKEN, refresh_token=FAKE_REFRESH_TOKEN, expires_in=3600
):
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": expires_in,
        "token_type": "JWT",
    }


def _v3_courses_response(courses=None, archived=None):
    """Return a v3 courses response (active + archived, no pagination)."""
    return {
        "courses": courses
        or [
            {
                "course_key": "course-v1:edX+E2E-101+course",
                "display_name": "E2E Test Course",
                "lms_link": "//lms.example.com/courses/course-v1:edX+E2E-101+course",
                "number": "E2E-101",
                "org": "edX",
                "rerun_link": "/course_rerun/course-v1:edX+E2E-101+course",
                "run": "course",
                "url": "/course/course-v1:edX+E2E-101+course",
            }
        ],
        "archived_courses": archived or [],
        "in_process_course_actions": [],
    }


def _v4_courses_response(courses=None):
    """Return a v4 paginated courses response (ADR 0032 envelope)."""
    if courses is None:
        courses = [
            {
                "course_key": "course-v1:edX+E2E-101+course",
                "display_name": "E2E Test Course",
                "lms_link": "//lms.example.com/courses/course-v1:edX+E2E-101+course",
                "cms_link": "//studio.example.com/course/course-v1:edX+E2E-101+course",
                "number": "E2E-101",
                "org": "edX",
                "rerun_link": "/course_rerun/course-v1:edX+E2E-101+course",
                "run": "course",
                "url": "/course/course-v1:edX+E2E-101+course",
                "is_active": True,
            }
        ]
    return {
        "count": len(courses),
        "num_pages": 1,
        "current_page": 1,
        "start": 0,
        "next": None,
        "previous": None,
        "results": {
            "courses": courses,
            "in_process_course_actions": [],
        },
    }


# ---------------------------------------------------------------------------
# JwtAuth unit tests
# ---------------------------------------------------------------------------


class TestJwtAuth:
    """Tests for the JwtAuth token handler."""

    # JwtAuth internals (_get_token, _expires_at) are the unit under test here.
    # pylint: disable=protected-access

    @rsps.activate
    def test_acquires_token_on_first_request(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())

        auth = JwtAuth(LMS_BASE, CLIENT_ID, CLIENT_SECRET)
        token = auth._get_token()

        assert token == FAKE_TOKEN
        assert len(rsps.calls) == 1

    @rsps.activate
    def test_reuses_token_within_expiry_buffer(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())

        auth = JwtAuth(LMS_BASE, CLIENT_ID, CLIENT_SECRET)
        auth._get_token()
        auth._get_token()  # second call should NOT hit the token endpoint

        assert len(rsps.calls) == 1

    @rsps.activate
    def test_refreshes_when_token_near_expiry(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response(access_token="new-token"))

        auth = JwtAuth(LMS_BASE, CLIENT_ID, CLIENT_SECRET)
        auth._get_token()

        # Force token to appear near expiry
        auth._expires_at = time.time() + 60  # only 60s left, below 300s buffer

        new_token = auth._get_token()

        assert new_token == "new-token"
        assert len(rsps.calls) == 2  # initial auth + refresh

    @rsps.activate
    def test_raises_on_auth_failure(self):
        rsps.add(rsps.POST, TOKEN_URL, status=401, json={"error": "invalid_client"})

        auth = JwtAuth(LMS_BASE, CLIENT_ID, CLIENT_SECRET)
        with pytest.raises(AuthenticationError):
            auth._get_token()

    @rsps.activate
    def test_falls_back_to_auth_when_refresh_fails(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(rsps.POST, TOKEN_URL, status=400, json={"error": "invalid_grant"})
        rsps.add(
            rsps.POST, TOKEN_URL, json=_token_response(access_token="re-auth-token")
        )

        auth = JwtAuth(LMS_BASE, CLIENT_ID, CLIENT_SECRET)
        auth._get_token()
        auth._expires_at = time.time() + 60

        token = auth._get_token()

        assert token == "re-auth-token"
        assert len(rsps.calls) == 3


# ---------------------------------------------------------------------------
# HomeResourceV3 tests
# ---------------------------------------------------------------------------


class TestHomeResourceV3:
    """Tests for the HomeResourceV3 (v3 endpoint — no pagination)."""

    @rsps.activate
    def test_courses_returns_active_and_archived(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(rsps.GET, V3_COURSES_URL, json=_v3_courses_response())

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v3.courses()

        assert "courses" in result
        assert "archived_courses" in result
        assert "in_process_course_actions" in result
        assert result["courses"][0]["course_key"] == "course-v1:edX+E2E-101+course"

    @rsps.activate
    def test_courses_passes_org_filter(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(
            rsps.GET,
            V3_COURSES_URL,
            match=[matchers.query_param_matcher({"org": "edX"})],
            json=_v3_courses_response(),
        )

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v3.courses(org="edX")

        assert "courses" in result

    @rsps.activate
    def test_libraries_returns_list(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(rsps.GET, V3_LIBRARIES_URL, json={"libraries": []})

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v3.libraries()

        assert "libraries" in result

    @rsps.activate
    def test_libraries_passes_is_migrated_filter(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(
            rsps.GET,
            V3_LIBRARIES_URL,
            match=[matchers.query_param_matcher({"is_migrated": "true"})],
            json={"libraries": []},
        )

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v3.libraries(is_migrated=True)

        assert "libraries" in result

    @rsps.activate
    def test_get_returns_aggregated_context(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(
            rsps.GET,
            V3_HOME_URL,
            json={
                "courses": [],
                "archived_courses": [],
                "libraries": [],
                "studio_name": "Studio",
            },
        )

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v3.get()

        assert "studio_name" in result

    @rsps.activate
    def test_courses_raises_api_error_on_non_2xx(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(rsps.GET, V3_COURSES_URL, status=401, body="Unauthorized")

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        with pytest.raises(ApiError) as exc_info:
            client.home.v3.courses()

        assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# HomeResourceV4 tests
# ---------------------------------------------------------------------------


class TestHomeResourceV4:
    """Tests for the HomeResourceV4 (v4 endpoint — paginated, ADR 0032)."""

    @rsps.activate
    def test_courses_returns_parsed_json(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(rsps.GET, V4_COURSES_URL, json=_v4_courses_response())

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v4.courses()

        assert "results" in result
        assert "courses" in result["results"]
        assert (
            result["results"]["courses"][0]["course_key"]
            == "course-v1:edX+E2E-101+course"
        )
        assert result["results"]["courses"][0]["is_active"] is True

    @rsps.activate
    def test_courses_returns_pagination_envelope(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(rsps.GET, V4_COURSES_URL, json=_v4_courses_response())

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v4.courses()

        for key in (
            "count",
            "num_pages",
            "current_page",
            "start",
            "next",
            "previous",
            "results",
        ):
            assert key in result

    @rsps.activate
    def test_courses_passes_org_filter(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(
            rsps.GET,
            V4_COURSES_URL,
            match=[matchers.query_param_matcher({"org": "edX"})],
            json=_v4_courses_response(),
        )

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v4.courses(org="edX")

        assert "results" in result

    @rsps.activate
    def test_courses_passes_search_filter(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(
            rsps.GET,
            V4_COURSES_URL,
            match=[matchers.query_param_matcher({"search": "E2E"})],
            json=_v4_courses_response(),
        )

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v4.courses(search="E2E")

        assert "results" in result

    @rsps.activate
    def test_courses_passes_ordering(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(
            rsps.GET,
            V4_COURSES_URL,
            match=[matchers.query_param_matcher({"ordering": "display_name"})],
            json=_v4_courses_response(),
        )

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v4.courses(ordering="display_name")

        assert "results" in result

    @rsps.activate
    def test_courses_passes_active_only_filter(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(
            rsps.GET,
            V4_COURSES_URL,
            match=[matchers.query_param_matcher({"active_only": "true"})],
            json=_v4_courses_response(),
        )

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v4.courses(active_only=True)

        assert "results" in result

    @rsps.activate
    def test_courses_passes_archived_only_filter(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(
            rsps.GET,
            V4_COURSES_URL,
            match=[matchers.query_param_matcher({"archived_only": "true"})],
            json=_v4_courses_response(courses=[]),
        )

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v4.courses(archived_only=True)

        assert result["results"]["courses"] == []

    @rsps.activate
    def test_courses_passes_pagination_params(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(
            rsps.GET,
            V4_COURSES_URL,
            match=[matchers.query_param_matcher({"page": "2", "page_size": "5"})],
            json=_v4_courses_response(),
        )

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        result = client.home.v4.courses(page=2, page_size=5)

        assert "results" in result

    @rsps.activate
    def test_courses_raises_api_error_on_non_2xx(self):
        rsps.add(rsps.POST, TOKEN_URL, json=_token_response())
        rsps.add(rsps.GET, V4_COURSES_URL, status=403, body="Forbidden")

        client = OpenEdxClient(
            LMS_BASE, CLIENT_ID, CLIENT_SECRET, studio_base=STUDIO_BASE
        )
        with pytest.raises(ApiError) as exc_info:
            client.home.v4.courses()

        assert exc_info.value.status_code == 403
