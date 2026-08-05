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

Backward Incompatibilities
--------------------------

Deprecations
------------

Documentation Changes
---------------------

