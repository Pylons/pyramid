unreleased
==========

Features
--------

- Add `Configurator.resolve_asset` and `Request.resolve_asset` methods.  See
  https://github.com/Pylons/pyramid/pull/3815.
- Replace all runtime usage of ``pkg_resources`` with :mod:`importlib.resources`.
  Pyramid no longer requires ``setuptools`` as a runtime dependency.
- Add :func:`pyramid.path.resource_filename` and :func:`pyramid.path.ref_filename`
  helpers for legacy filesystem access to package resources.
- Move :class:`pyramid.resolver.AssetResolver` and
  :class:`pyramid.resolver.DottedNameResolver` to the new
  :mod:`pyramid.resolver` module (still re-exported from :mod:`pyramid.path`).

Bug Fixes
---------

Backward Incompatibilities
--------------------------

- Asset overrides registered via
  :meth:`pyramid.config.Configurator.override_asset` are no longer visible to
  third-party code that calls ``pkg_resources`` APIs directly.  Overrides are
  now applied explicitly by Pyramid's own asset resolution APIs (such as
  :class:`pyramid.resolver.AssetResolver`).
- :class:`pyramid.interfaces.IPackageOverrides` no longer extends
  :class:`pyramid.interfaces.IPEP302Loader`.  The ``OverrideProvider`` class
  and ``register_loader_type`` integration have been removed.
- :class:`pyramid.config.assets.PackageOverrides` no longer sets
  ``package.__loader__``.

Deprecations
------------

Documentation Changes
---------------------

- Update asset resolution documentation to describe ``importlib.resources``
  instead of ``pkg_resources``.
