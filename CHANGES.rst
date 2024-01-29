unreleased
==========

Features
--------

- Pyramid adds support for Python 3.11.

- Added HTTP 418 error code via `pyramid.httpexceptions.HTTPImATeapot`.
  See https://github.com/Pylons/pyramid/pull/3667

- Coverage reports in tests based on Python 3.11 instead of Python 3.8.

- Added `LIFT` sentinel value that may be used for context and name arguments
  to view_config on class methods in conjunction with venusian lift.

Bug Fixes
---------

- Removed support for null-bytes in the path when making a request for a file
  against a static_view. Whille null-bytes are allowed by the HTTP
  specification, due to the handling of null-bytes potentially leading to
  security vulnerabilities it is no longer supported.

  This fixes a security vulnerability that is present due to a bug in Python
  3.11.0 through 3.11.4, thereby allowing the unintended disclosure of an
  ``index.html`` one directory up from the static views path.

  Thanks to Masashi Yamane of LAC Co., Ltd for reporting this issue.

Backward Incompatibilities
--------------------------

- Requests to a static_view are no longer allowed to contain a null-byte in any
  part of the path segment.
- Pyramid is no longer tested on, nor supports Python 3.6
- Pyramid drops support for l*gettext() methods in the i18n module.
  These have been deprecated in Python's gettext module since 3.8, and
  removed in Python 3.11.

Documentation Changes
---------------------
