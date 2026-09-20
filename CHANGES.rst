unreleased
==========

Features
--------

- Add `Configurator.resolve_asset` and `Request.resolve_asset` methods.  See
  https://github.com/Pylons/pyramid/pull/3815.

Bug Fixes
---------

- Correct the ``pop`` declaration on the documentation-only
  ``pyramid.interfaces.IDict``.  It was declared ``pop(k, default=None)``,
  which contradicts its own docstring: with a default always bound, the
  KeyError case it describes cannot arise.  It now reads ``pop(k, *args)``,
  matching ``dict.pop``.  Also correct the ``popitem`` docstring, which
  referred to a key ``k`` that the method does not take.  See
  https://github.com/Pylons/pyramid/issues/3237.

Backward Incompatibilities
--------------------------

Deprecations
------------

Documentation Changes
---------------------

