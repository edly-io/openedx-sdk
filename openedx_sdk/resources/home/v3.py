"""
Resource for the Studio home endpoints (v3).

Covers HomeViewSet (ADR 0028) registered at:
  GET /api/contentstore/v3/home/           → aggregated home context
  GET /api/contentstore/v3/home/courses/   → courses list
  GET /api/contentstore/v3/home/libraries/ → libraries list
"""

from ...exceptions import ApiError

_BASE_PATH = "/api/contentstore/v3/home"


class HomeResourceV3:
    """
    Provides access to the Studio home API endpoints (v3).

    Do not instantiate directly — use :class:`openedx_sdk.OpenEdxClient`.

    Example::

        client = OpenEdxClient(lms_base=..., client_id=..., client_secret=...)

        # Aggregated home context (courses + libraries + Studio settings)
        home = client.home.v3.get()

        # Courses only (active + archived, no pagination)
        result = client.home.v3.courses(org="edX")
        for course in result["courses"]:
            print(course["display_name"])
        for course in result["archived_courses"]:
            print(course["display_name"], "(archived)")

        # Libraries only
        result = client.home.v3.libraries()
        result = client.home.v3.libraries(is_migrated=True)
    """

    def __init__(self, session, studio_base):
        self._session = session
        self._base_url = studio_base.rstrip("/") + _BASE_PATH

    def get(self, org=None):
        """
        Return the Studio home context (courses, libraries, and settings).

        Maps to ``GET /api/contentstore/v3/home/``
        (HomeViewSet.list — ADR 0028).

        :param org: Optional org slug to filter results.
        :returns: dict with ``courses``, ``archived_courses``, ``libraries``,
                  ``in_process_course_actions``, and various Studio settings
                  such as ``studio_name``, ``platform_name``,
                  ``user_is_active``.
        :raises ~openedx_sdk.exceptions.ApiError: on non-2xx response.

        Response shape (partial)::

            {
                "courses": [...],
                "archived_courses": [...],
                "libraries": [...],
                "in_process_course_actions": [],
                "studio_name": "Studio",
                "platform_name": "Your Platform Name",
                "user_is_active": true,
                ...
            }
        """
        params = {"org": org} if org else None
        return self._get(f"{self._base_url}/", params=params)

    def courses(self, org=None):
        """
        Return the list of active, archived, and in-progress courses.

        Maps to ``GET /api/contentstore/v3/home/courses/``
        (HomeViewSet.courses action — ADR 0028).

        :param org: Optional org slug to filter results.
        :returns: dict with keys ``courses``, ``archived_courses``,
                  and ``in_process_course_actions``.
        :raises ~openedx_sdk.exceptions.ApiError: on non-2xx response.

        Response shape::

            {
                "courses": [
                    {
                        "course_key": "course-v1:edX+E2E-101+course",
                        "display_name": "E2E Test Course",
                        "lms_link": "//lms.example.com/courses/...",
                        "number": "E2E-101",
                        "org": "edX",
                        "rerun_link": "/course_rerun/...",
                        "run": "course",
                        "url": "/course/course-v1:edX+E2E-101+course"
                    }
                ],
                "archived_courses": [...],
                "in_process_course_actions": []
            }
        """
        params = {"org": org} if org else None
        return self._get(f"{self._base_url}/courses/", params=params)

    def libraries(self, org=None, is_migrated=None):
        """
        Return the list of libraries.

        Maps to ``GET /api/contentstore/v3/home/libraries/``
        (HomeViewSet.libraries action — ADR 0028).

        :param org: Optional org slug to filter results.
        :param is_migrated: Optional bool — ``True`` returns only libraries
                            migrated to v2; ``False`` returns only
                            non-migrated.
                            Omit to return all libraries.
        :returns: dict with key ``libraries``.
        :raises ~openedx_sdk.exceptions.ApiError: on non-2xx response.

        Response shape::

            {
                "libraries": [
                    {
                        "library_key": "lib:edX:mylib",
                        "display_name": "My Library",
                        ...
                    }
                ]
            }
        """
        params = {}
        if org:
            params["org"] = org
        if is_migrated is not None:
            params["is_migrated"] = "true" if is_migrated else "false"
        return self._get(f"{self._base_url}/libraries/", params=params or None)

    def _get(self, url, params=None):
        """Make a GET request and return the parsed JSON response."""
        response = self._session.get(url, params=params)
        if not response.ok:
            raise ApiError(response.status_code, response.text)
        return response.json()
