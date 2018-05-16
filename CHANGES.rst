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

- In ``cherrypy_server_runner``, prefer imports from the ``cheroot`` package over the legacy
  imports from `cherrypy.wsgiserver`.
  See https://github.com/Pylons/pyramid/pull/3235

Bug Fixes
---------

- Set appropriate ``code`` and ``title`` attributes on the ``HTTPClientError`` and
  ``HTTPServerError`` exception classes. This prevents inadvertently returning a 520
  error code.
  See https://github.com/Pylons/pyramid/pull/3280

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

- Bump Sphinx to >= 1.7.4 in setup.py to support ``emphasize-lines`` in PDFs
  and to pave the way for xelatex support.  See
  https://github.com/Pylons/pyramid/pull/3271,
  https://github.com/Pylons/pyramid/issues/667, and
  https://github.com/Pylons/pyramid/issues/2572
