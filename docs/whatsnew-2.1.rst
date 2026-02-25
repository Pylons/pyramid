What's New in Pyramid 2.1
=========================

This article explains the new features in :app:`Pyramid` version 2.1 as compared to its predecessor, :app:`Pyramid` 2.0.
It also documents backwards incompatibilities between the two versions and deprecations added to :app:`Pyramid` 2.1, as well as software dependency changes and notable documentation additions.

Major Feature Additions
-----------------------

- Add support for Python 3.12, 3.13, and 3.14.

- Constrain ``setuptools < 82`` to remain compatible with required ``pkg_resources`` features.
  Work continues to fully remove ``pkg_resources`` from Pyramid code in future releases.
  See https://github.com/Pylons/pyramid/pull/3795

- Added HTTP 418 error code via :class:`pyramid.httpexceptions.HTTPImATeapot`.
  See https://github.com/Pylons/pyramid/pull/3667

- All scripts now pass a new option ``__script__`` when loading the WSGI app.
  For example, ``pserve`` sets ``__script__ == 'pserve'``.
  This works for ``pserve``, ``pshell``, ``prequest``, ``proutes``, ``ptweens``, ``pviews``, as well as when using :func:`pyramid.paster.bootstrap` directly.

  When using ``plaster-pastedeploy`` to load an INI file, this option will manifest as a new value passed into the ``global_conf`` arg of your application factory, where you can use it as part of initializing your app.

  See https://github.com/Pylons/pyramid/pull/3735

Minor Feature Additions
-----------------------

- Base coverage reports in tests on Python 3.14 instead of Python 3.8.

- Replace usage of ``md5`` in the Pyramid view system with ``sha256``.
  This is not a security-related feature and is considered an implementation detail that should not impact users.

  See https://github.com/Pylons/pyramid/pull/3745

- Replace usage of ``pkg_resources`` in :class:`pyramid.path.DottedNameResolver`.
  See https://github.com/Pylons/pyramid/pull/3748

- Replace usage of ``pkg_resources`` in ``pdistreport`` and ``pshell`` CLI commands.
  See https://github.com/Pylons/pyramid/pull/3749

- Remove internal usages of deprecated ``locale`` and ``datetime`` APIs to reduce deprecation warnings.
  See https://github.com/Pylons/pyramid/pull/3808

Deprecations
------------

- Deprecated the ability to use a non-existent package with :meth:`pyramid.config.Configurator.add_static_view` and :class:`pyramid.static.static_view`.
  This can be fixed by choosing a path located within a real package as the ``root_dir`` for your static files.
  This is almost always either a misconfig or an attempt to define an alias location for use with :meth:`pyramid.config.Configurator.override_asset`.
  See https://github.com/Pylons/pyramid/pull/3752

Backward Incompatibilities
--------------------------

- Drop support for Python 3.6, 3.7, 3.8, and 3.9.

- Drop support for l*gettext() methods in the i18n module.
  These have been deprecated in Python's gettext module since 3.8, and removed in Python 3.11.

- Add `get_spec` method to :class:`pyramid.interfaces.IPackageOverrides`.
  See https://github.com/Pylons/pyramid/pull/3792

- When using a cache buster with asset overrides, the cache buster will find the first existing file in the override stack, rather than taking the first override regardless of whether the file exists or not.
  See https://github.com/Pylons/pyramid/pull/3792

Documentation Enhancements
--------------------------

- Sync the SQLAlchemy Wiki tutorial with changes to the ``pyramid-cookiecutter-starter``.
  Includes updates to use ``pyproject.toml`` to replace separate config files for ``pytest``, ``coverage``, and ``setuptools``.
  Also upgrades patterns to support SQLAlchemy 2.0.
  See https://github.com/Pylons/pyramid/pull/3747

- Sync the ZODB Wiki tutorial with changes to the ``pyramid-cookiecutter-starter``.
  Includes updates to use ``pyproject.toml`` to replace separate config files for ``pytest``, ``coverage``, and ``setuptools``.
  See https://github.com/Pylons/pyramid/pull/3751
