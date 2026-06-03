openedx-sdk
###########

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

``openedx-sdk`` is the official Python client library for the Open edX REST APIs.
It is part of the `Open edX API standardization project`_ and provides a simple,
authenticated interface to Open edX platform endpoints.

It handles OAuth2 JWT authentication (token acquisition and automatic refresh)
transparently, so you can focus on your integration rather than token management.

.. _Open edX API standardization project: https://github.com/openedx/openedx-platform/tree/docs/ADRs-axim_api_improvements

Installation
************

The package is not yet published on PyPI. Install directly from GitHub:

.. code-block:: bash

    pip install git+https://github.com/edly-io/openedx-sdk.git@master

Quick Start
***********

**1. Create an OAuth2 client** in your Open edX LMS at
``/admin/oauth2_provider/application/`` with grant type ``Client credentials``.

**2. Use the client:**

Resources are grouped by area, then version (e.g. ``client.home.v4``):

.. code-block:: python

    from openedx_sdk import OpenEdxClient

    client = OpenEdxClient(
        lms_base="https://lms.example.com",
        client_id="your-client-id",
        client_secret="your-client-secret",
        studio_base="https://studio.example.com",  # optional, defaults to lms_base
    )

    # v4 — paginated courses (ADR 0032)
    data = client.home.v4.courses(org="edX", page=1, page_size=20)
    for course in data["results"]["courses"]:
        print(course["display_name"], course["course_key"], course["is_active"])

    # v4 — search and filter
    active = client.home.v4.courses(active_only=True, ordering="display_name")
    results = client.home.v4.courses(search="intro")

    # v3 — courses with active + archived split (no pagination)
    data = client.home.v3.courses(org="edX")
    for course in data["courses"]:
        print(course["display_name"])
    for course in data["archived_courses"]:
        print(course["display_name"], "(archived)")

    # v3 — libraries
    libs = client.home.v3.libraries()
    migrated = client.home.v3.libraries(is_migrated=True)

    # v3 — aggregated home context (courses + libraries + Studio settings)
    home = client.home.v3.get()

Authentication
**************

The SDK uses OAuth2 ``client_credentials`` grant to obtain a JWT from
``/oauth2/access_token/``. Tokens are cached and refreshed automatically
(using ``grant_type=refresh_token``) before they expire — you never need
to manage tokens manually.

Available Resources
*******************

+------------+--------------------------------------------------+------------------------------------------------+
| Namespace  | Method                                           | Endpoint                                       |
+============+==================================================+================================================+
| ``home.v4``| ``courses(org, search, ordering,``               | ``GET /api/contentstore/v4/home/courses/``     |
|            | ``active_only, archived_only, page, page_size)`` |                                                |
+------------+--------------------------------------------------+------------------------------------------------+
| ``home.v3``| ``courses(org)``                                 | ``GET /api/contentstore/v3/home/courses/``     |
+------------+--------------------------------------------------+------------------------------------------------+
| ``home.v3``| ``libraries(org, is_migrated)``                  | ``GET /api/contentstore/v3/home/libraries/``   |
+------------+--------------------------------------------------+------------------------------------------------+
| ``home.v3``| ``get(org)``                                     | ``GET /api/contentstore/v3/home/``             |
+------------+--------------------------------------------------+------------------------------------------------+

**v4 response** follows the ADR 0032 pagination envelope:

.. code-block:: python

    {
        "count": 42, "num_pages": 5, "current_page": 1, "start": 0,
        "next": "...", "previous": null,
        "results": {
            "courses": [{"course_key": "...", "is_active": true, ...}],
            "in_process_course_actions": []
        }
    }

**v3 courses response** (no pagination, active + archived split):

.. code-block:: python

    {
        "courses": [{"course_key": "...", ...}],
        "archived_courses": [...],
        "in_process_course_actions": []
    }

Error Handling
**************

.. code-block:: python

    from openedx_sdk import OpenEdxClient, ApiError, AuthenticationError

    client = OpenEdxClient(...)

    try:
        data = client.home.v4.courses(org="edX")
        for course in data["results"]["courses"]:
            print(course["display_name"])
    except AuthenticationError as e:
        print(f"Could not authenticate: {e}")
    except ApiError as e:
        print(f"API returned HTTP {e.status_code}: {e}")

Getting Started with Development
*********************************

.. code-block:: bash

    git clone https://github.com/openedx/openedx-sdk.git
    cd openedx-sdk
    pip install requests responses pytest pytest-cov
    pip install -e .
    pytest tests/

Please see the Open edX documentation for `guidance on Python development`_ in this repo.

.. _guidance on Python development: https://docs.openedx.org/en/latest/developers/how-tos/get-ready-for-python-dev.html

Getting Help
************

Documentation
=============

Start by going through `the documentation`_.

.. _the documentation: https://docs.openedx.org/projects/openedx-sdk

More Help
=========

If you're having trouble, we have discussion forums at
https://discuss.openedx.org where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this
repository with as many details about the issue you are facing as you
can provide.

https://github.com/openedx/openedx-sdk/issues

For more information about these options, see the `Getting Help <https://openedx.org/getting-help>`__ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to discuss your new feature idea with the maintainers before beginning development
to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://backstage.openedx.org/catalog/default/component/openedx-sdk

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/openedx-sdk.svg
    :target: https://pypi.python.org/pypi/openedx-sdk/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/openedx/openedx-sdk/actions/workflows/ci.yml/badge.svg?branch=main
    :target: https://github.com/openedx/openedx-sdk/actions/workflows/ci.yml
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/openedx/openedx-sdk/coverage.svg?branch=main
    :target: https://codecov.io/github/openedx/openedx-sdk?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/openedx-sdk/badge/?version=latest
    :target: https://docs.openedx.org/projects/openedx-sdk
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/openedx-sdk.svg
    :target: https://pypi.python.org/pypi/openedx-sdk/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/openedx/openedx-sdk.svg
    :target: https://github.com/openedx/openedx-sdk/blob/main/LICENSE.txt
    :alt: License

.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
