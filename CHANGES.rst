unreleased
==========

Features
--------

- Add support for Python 3.12.

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

- Replace usage of ``md5`` in the Pyramid view system with ``sha256``. This
  is not a security-related feature and is considered an implementation detail
  that should not impact users.

  See https://github.com/Pylons/pyramid/pull/3745

- Replace usage of ``pkg_resources`` in ``pyramid.path.DottedNameResolver``.
  See https://github.com/Pylons/pyramid/pull/3748

Bug Fixes
---------

- Fix issues where permissions may be checked on exception views. This is not
  supposed to happen in normal circumstances.

  This also prevents issues where a ``request.url`` fails to be decoded when
  logging info when ``pyramid.debug_authorization`` is enabled.

  See https://github.com/Pylons/pyramid/pull/3741/files

- Applications raising ``pyramid.exceptions.BadCSRFToken`` and
  ``pyramid.exceptions.BadCSRFOrigin`` were returning invalid HTTP status
  lines with values like ``400 Bad CSRF Origin`` instead of
  ``400 Bad Request``.

  See https://github.com/Pylons/pyramid/pull/3742

Backward Incompatibilities
--------------------------

- Drop support for Python 3.6 and 3.7.

- Drop support for l*gettext() methods in the i18n module.
  These have been deprecated in Python's gettext module since 3.8, and
  removed in Python 3.11.

Documentation Changes
---------------------
