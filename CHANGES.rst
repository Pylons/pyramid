unreleased
==========

Features
--------

- Add `Configurator.resolve_asset` and `Request.resolve_asset` methods.  See
  https://github.com/Pylons/pyramid/pull/3815.

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
  referred to a key ``k`` that the method does not take.  See
  https://github.com/Pylons/pyramid/issues/3237.

Backward Incompatibilities
--------------------------

Deprecations
------------

Documentation Changes
---------------------

- Improve rendering of API Documentation by removing the prefixes to APIs in the sidebar.
  See https://github.com/Pylons/pyramid/pull/3834
