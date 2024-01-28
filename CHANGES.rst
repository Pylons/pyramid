unreleased
==========

Features
--------

- Add support for Python 3.11 and 3.12.

- Added HTTP 418 error code via `pyramid.httpexceptions.HTTPImATeapot`.
  See https://github.com/Pylons/pyramid/pull/3667

- Coverage reports in tests based on Python 3.12 instead of Python 3.8.

- All scripts now pass a new option ``__script__`` when loading the WSGI app.
  For example, ``pserve`` sets ``__script__ == 'pserve'``. This works for
  ``pserve``, ``pshell``, ``prequest``, ``proutes``, ``ptweens``, ``pviews``,
  as well as when using ``pyramid.paster.bootstrap`` directly.

  When using ``plaster-pastedeploy`` to load an INI file, this option will
  manifest as a new value passed into the ``global_conf`` arg of your
  application factory, where you can use it as part of initializing your app.

  See https://github.com/Pylons/pyramid/pull/3735

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

- Drop support for Python 3.6.

- Requests to a static_view are no longer allowed to contain a null-byte in any
  part of the path segment.

- Drop support for l*gettext() methods in the i18n module.
  These have been deprecated in Python's gettext module since 3.8, and
  removed in Python 3.11.

Documentation Changes
---------------------
