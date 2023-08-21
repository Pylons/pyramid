unreleased
==========

Features
--------

- Pyramid adds support for Python 3.11.

- Added HTTP 418 error code via `pyramid.httpexceptions.HTTPImATeapot`.
  See https://github.com/Pylons/pyramid/pull/3667

- Coverage reports in tests based on Python 3.11 instead of Python 3.8.

Bug Fixes
---------

Backward Incompatibilities
--------------------------

- Pyramid is no longer tested on, nor supports Python 3.6
- Pyramid drops support for l*gettext() methods in the i18n module.
  These have been deprecated in Python's gettext module since 3.8, and
  removed in Python 3.11.

Documentation Changes
---------------------
