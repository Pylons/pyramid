unreleased
==========

Features
--------

- Add a ``_depth`` and ``_category`` arguments to all of the venusian
  decorators. The ``_category`` argument can be used to affect which actions
  are registered when performing a ``config.scan(..., category=...)`` with a
  specific category. The ``_depth`` argument should be used when wrapping
  the decorator in your own. This change affects ``pyramid.view.view_config``,
  ``pyramid.view.exception_view_config``,
  ``pyramid.view.forbidden_view_config``, ``pyramid.view.notfound_view_config``,
  ``pyramid.events.subscriber`` and ``pyramid.response.response_adapter``
  decorators. See https://github.com/Pylons/pyramid/pull/3105 and
  https://github.com/Pylons/pyramid/pull/3122

- Fix the ``pyramid.request.Request`` class name after using
  ``set_property`` or ``config.add_request_method`` such that the
  ``str(request.__class__)`` would appear as ``pyramid.request.Request``
  instead of ``pyramid.util.Request``.
  See https://github.com/Pylons/pyramid/pull/3129

Bug Fixes
---------

Deprecations
------------

Backward Incompatibilities
--------------------------

- On Python 3.4+ the ``repoze.lru`` dependency is dropped. If you were using
  this package directly in your apps you should make sure that you are
  depending on it directly within your project.
  See https://github.com/Pylons/pyramid/pull/3140

Documentation Changes
---------------------

