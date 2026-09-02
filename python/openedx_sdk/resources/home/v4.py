"""
Resource for the Studio home courses endpoint (v4).

Covers HomeCoursesViewSet (ADR 0028) registered at:
  GET /api/contentstore/v4/home/courses/

Supports pagination (ADR 0032), filtering, and ordering (ADR 0033).
"""

from ...resources.base import BaseResource

_BASE_PATH = "/api/contentstore/v4/home/courses"


class HomeResourceV4(BaseResource):
    """
    Provides access to the Studio home courses API (v4).

    Do not instantiate directly — use :class:`openedx_sdk.OpenEdxClient`.

    Example::

        client = OpenEdxClient(lms_base=..., client_id=..., client_secret=...)

        # All courses (paginated)
        result = client.home.v4.courses()
        for course in result["results"]["courses"]:
            print(course["display_name"])

        # Filter by org and paginate
        result = client.home.v4.courses(org="edX", page=2, page_size=20)

        # Search
        result = client.home.v4.courses(search="intro")

        # Active courses only, ordered by display name
        result = client.home.v4.courses(
            active_only=True, ordering="display_name"
        )
    """

    def __init__(self, session, studio_base):
        super().__init__(session)
        self._base_url = studio_base.rstrip("/") + _BASE_PATH

    def courses(
        self,
        *,
        org=None,
        search=None,
        ordering=None,
        active_only=None,
        archived_only=None,
        page=None,
        page_size=None,
    ):
        """
        Return a paginated list of courses visible to the authenticated user.

        Maps to ``GET /api/contentstore/v4/home/courses/``
        (HomeCoursesViewSet.list — ADR 0028, 0032, 0033).

        :param org: Optional org slug to filter results.
        :param search: Optional string to filter by course name, org, or
                       number.
        :param ordering: Sort field: ``display_name``, ``org``, ``number``,
                         or ``run``. Prefix with ``-`` for descending order.
        :param active_only: If ``True``, return only active (non-archived)
                            courses.
        :param archived_only: If ``True``, return only archived courses.
        :param page: Page number to retrieve (default 1).
        :param page_size: Number of courses per page (default 10, max 100).
        :returns: Paginated response dict (ADR 0032) with keys
                  ``count``, ``num_pages``, ``current_page``, ``start``,
                  ``next``, ``previous``, and ``results``.
                  ``results`` contains ``courses`` (each with an ``is_active``
                  flag) and ``in_process_course_actions``.
        :raises ~openedx_sdk.exceptions.ApiError: on non-2xx response.

        Response shape::

            {
                "count": 1,
                "num_pages": 1,
                "current_page": 1,
                "start": 0,
                "next": null,
                "previous": null,
                "results": {
                    "courses": [
                        {
                            "course_key": "course-v1:edX+E2E-101+course",
                            "display_name": "E2E Test Course",
                            "lms_link": "//lms.example.com/courses/...",
                            "cms_link": "//studio.example.com/course/...",
                            "number": "E2E-101",
                            "org": "edX",
                            "rerun_link": "/course_rerun/...",
                            "run": "course",
                            "url": "/course/course-v1:edX+E2E-101+course",
                            "is_active": true
                        }
                    ],
                    "in_process_course_actions": []
                }
            }
        """
        params = {}
        if org:
            params["org"] = org
        if search:
            params["search"] = search
        if ordering:
            params["ordering"] = ordering
        if active_only is not None:
            params["active_only"] = "true" if active_only else "false"
        if archived_only is not None:
            params["archived_only"] = "true" if archived_only else "false"
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        return self._get(f"{self._base_url}/", params=params or None)
