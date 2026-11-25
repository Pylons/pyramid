unreleased
==========

Features
--------

- Remove ``setuptools`` as a dependency.
  See https://github.com/Pylons/pyramid/pull/3847

- Add ``Configurator.resolve_asset`` and ``Request.resolve_asset`` methods.
  See https://github.com/Pylons/pyramid/pull/3815

- Add asset specification support to ``pyramid.response.FileResponse``.
  See https://github.com/Pylons/pyramid/pull/3836

- Add support for Python 3.15.
  See https://github.com/Pylons/pyramid/pull/3840

- Speed up configuration conflict resolution during ``config.commit()`` and
  ``config.make_wsgi_app()``. Actions are no longer removed from the pending
  list one at a time, which was quadratic in the number of actions and slowed
  startup noticeably for applications with thousands of routes and views.
  Thanks to Russell Ballestrini for the original patch.
  See https://github.com/Pylons/pyramid/pull/NNNN

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

- ``setuptools`` has been removed as a dependency.
  If your application depends on ``setuptools``, be sure to add it as a direct dependency, specifying ``setuptools<82`` if you need ``pkg_resources``.
  If ``pkg_resources`` is present, Pyramid will register :ref:`asset overrides <overriding_assets_section>` as it has done previously.
  See https://github.com/Pylons/pyramid/pull/3847

- Assets are now loaded with ``importlib.resources`` instead of setuptools' ``pkg_resources``.
  Unlike the setuptools implementation, Pyramid does not hook into the machinery of ``importlib.resources`` and direct usage of the ``importlib.resources`` APIs will not honor :ref:`asset overrides <overriding_assets_section>`.
  Please use the new :ref:`asset APIs <accessing_assets>` for loading assets within your application.
  See https://github.com/Pylons/pyramid/pull/3843

- ``pyramid.path.PkgResourcesAssetDescriptor`` is now an alias of ``pyramid.path.ImportlibResourcesAssetDescriptor``.
  See https://github.com/Pylons/pyramid/pull/3843

- Replace ``pyramid.util.DottedNameResolver`` with a shim.  Users should use
  ``pyramid.path.DottedNameResolver`` instead.
  See https://github.com/Pylons/pyramid/pull/3837

Deprecations
------------

- Deprecate ``pyramid.util.DottedNameResolver`` in favor of
  ``pyramid.path.DottedNameResolver``.
  See https://github.com/Pylons/pyramid/pull/3837

- Deprecate ``pyramid.path.PkgResourcesAssetDescriptor``.
  See https://github.com/Pylons/pyramid/pull/3843

Documentation Changes
---------------------

- Improve rendering of API Documentation by removing the prefixes to APIs in the sidebar.
  See https://github.com/Pylons/pyramid/pull/3834
