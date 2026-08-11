unreleased
==========

Features
--------

- Add `Configurator.resolve_asset` and `Request.resolve_asset` methods.  See
  https://github.com/Pylons/pyramid/pull/3815.

Bug Fixes
---------

Backward Incompatibilities
--------------------------

Deprecations
------------

- Move ``AssetResolver``, ``DottedNameResolver``, ``FSAssetDescriptor``,
  ``PkgResourcesAssetDescriptor``, ``Resolver`` from ``pyramid.path`` to new
  ``pyramid.resolver`` module.  See
  https://github.com/Pylons/pyramid/issues/3731

Documentation Changes
---------------------

