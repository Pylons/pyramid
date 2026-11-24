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
- Remove ``pyramid.path.caller_path``.
  See https://github.com/Pylons/pyramid/pull/3849
- Remove ``pyramid.path.package_path``.
  See https://github.com/Pylons/pyramid/pull/3849
- Deprecate ``pyramid.asset.resolve_asset_spec``.
  Use the new :ref:`asset APIs <accessing_assets>` instead, which accept asset specifications directly and can make parsing specification strings unnecessary in many cases.
  See https://github.com/Pylons/pyramid/pull/3849
- Deprecate ``pyramid.asset.asset_spec_from_abspath``.
  Accessing package contents via file paths is discouraged, as the package may not exist in the filesystem and need to be unpacked to a temporary directory.
  There is no direct replacement; consider whether the new :ref:`asset APIs <accessing_assets>` can meet your needs.
  See https://github.com/Pylons/pyramid/pull/3849
- Deprecate ``pyramid.asset.abspath_from_asset_spec``.
  Use :meth:`pyramid.interfaces.IAssetDescriptor.abspath` via the new :ref:`asset APIs <accessing_assets>` instead, e.g., ``request.resolve_asset(spec).abspath()``.
  See https://github.com/Pylons/pyramid/pull/3849
- Deprecate ``pyramid.resource``.
  This has been a non-API backwards compatibility shim since Pyramid 1.0; importing it will now trigger a warning.
  See https://github.com/Pylons/pyramid/pull/3849

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
