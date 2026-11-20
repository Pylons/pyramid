unreleased
==========

Features
--------

- Add ``Configurator.resolve_asset`` and ``Request.resolve_asset`` methods.
  See https://github.com/Pylons/pyramid/pull/3815
- Add asset specification support to ``pyramid.response.FileResponse``.
  See https://github.com/Pylons/pyramid/pull/3836
- Add support for Python 3.15.
  See https://github.com/Pylons/pyramid/pull/3840

Bug Fixes
---------

- Avoid ``inspect.getfullargspec`` when checking view and subscriber
  callables so Python 3.14's deferred annotation evaluation does not resolve
  annotations that Pyramid does not use. See
  https://github.com/Pylons/pyramid/issues/3812

- Correct the ``pop`` declaration on the documentation-only
  ``pyramid.interfaces.IDict``.  It was declared ``pop(k, default=None)``,
  which contradicts its own docstring: with a default always bound, the
  KeyError case it describes cannot arise.  It now reads ``pop(k, *args)``,
  matching ``dict.pop``.  Also correct the ``popitem`` docstring, which
  referred to a key ``k`` that the method does not take.
  See https://github.com/Pylons/pyramid/issues/3237

- Fix a ``TypeError`` that occurred when using
  ``pyramid.authentication.RepozeWho1AuthenticationPolicy`` with debug logging enabled
  and the ``authenticated_userid`` was ``None``.
  See https://github.com/Pylons/pyramid/pull/3814

Backward Incompatibilities
--------------------------

- Drop support for Python 3.10, which reached end-of-life in October 2026.
  See https://github.com/Pylons/pyramid/pull/3840
- Drop testing on PyPy 3.11 in favor of PyPy 3.12.
  See https://github.com/Pylons/pyramid/pull/3840
- Replace ``pyramid.util.DottedNameResolver`` with a shim.  Users should use
  ``pyramid.path.DottedNameResolver`` instead.
  See https://github.com/Pylons/pyramid/pull/3837

Deprecations
------------

- Deprecate ``pyramid.util.DottedNameResolver`` in favor of
  ``pyramid.path.DottedNameResolver``.
  See https://github.com/Pylons/pyramid/pull/3837

Documentation Changes
---------------------

- Improve rendering of API Documentation by removing the prefixes to APIs in the sidebar.
  See https://github.com/Pylons/pyramid/pull/3834
