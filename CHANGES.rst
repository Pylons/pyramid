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

- Replace usage of ``pkg_resources`` in ``pdistreport`` and ``pshell`` CLI
  commands. See https://github.com/Pylons/pyramid/pull/3749

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

- When a bad settings URI (usually a path to a non-existant file) is
  supplied to one of pyramid's command line programs, and in general
  when there is a reason why a settings file cannot be used, produce
  an error message instead of a traceback.

  Applications which import pyramid.paster must handle the
  plaster.exceptions.PlasterError exception themselves.

Backward Incompatibilities
--------------------------

- Drop support for Python 3.6 and 3.7.

- Drop support for l*gettext() methods in the i18n module.
  These have been deprecated in Python's gettext module since 3.8, and
  removed in Python 3.11.

Deprecations
------------

- Deprecated the ability to use a non-existent package with
  ``pyramid.config.Configurator.add_static_view`` and
  ``pyramid.static.static_view``. This can be fixed by choosing a path
  located within a real package as the ``root_dir`` for your static files.
  This is almost always either a misconfig or an attempt to define an alias
  location for use with ``pyramid.config.Configurator.override_asset``.
  See https://github.com/Pylons/pyramid/pull/3752

Documentation Changes
---------------------

- Sync the SQLAlchemy Wiki tutorial with changes to the
  ``pyramid-cookiecutter-starter``. Includes updates to use ``pyproject.toml``
  to replace separate config files for ``pytest``, ``coverage``, and
  ``setuptools``. Also upgrades patterns to support SQLAlchemy 2.0.
  See https://github.com/Pylons/pyramid/pull/3747

- Sync the ZODB Wiki tutorial with changes to the
  ``pyramid-cookiecutter-starter``. Includes updates to use ``pyproject.toml``
  to replace separate config files for ``pytest``, ``coverage``, and
  ``setuptools``.
  See https://github.com/Pylons/pyramid/pull/3751
