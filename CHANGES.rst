Unreleased
==========

- Break potential reference cycle between `request` and `context`.
  See https://github.com/Pylons/pyramid/pull/3650

.. _changes_1.10.5:

1.10.5 (2020-11-08)
===================

- Support Python 3.8 and 3.9.

- Deprecate the default ``hashalg='md5'`` on
  ``pyramid.authentication.AuthTktCookieHelper`` to encourage users to be
  explicit if they want their code to work without changes when upgrading to
  Pyramid 2.0.

.. _changes_1.10.4:

1.10.4 (2019-04-15)
===================

- Fix performance regression in ``pyramid.view.view_config`` decorator.
  See https://github.com/Pylons/pyramid/pull/3490

.. _changes_1.10.3:

1.10.3 (2019-04-12)
===================

- Add ``ignore_files`` option to ``[pserve]`` settings which will tell
  ``pserve`` to ignore certain files/globs when using ``--reload``.
  See https://github.com/Pylons/pyramid/pull/3464

- Fix docs build for Sphinx 2.0.
  See https://github.com/Pylons/pyramid/pull/3481

- Improve debugging info from ``pyramid.view.view_config`` decorator.
  See https://github.com/Pylons/pyramid/pull/3485

.. _changes_1.10.2:

1.10.2 (2019-01-30)
===================

- Fix a bug in ``pyramid.testing.DummySecurityPolicy`` in which
  ``principals_allowed_by_permission`` would return all principals instead
  of an empty list if ``permissive`` is ``False``.
  See https://github.com/Pylons/pyramid/pull/3450

- Fix a bug in which ``pyramid.exceptions.ConfigurationConflictError`` may
  not render the appropriate error message on certain conflicts that were
  not sortable on Python 3 due to differing types.
  See https://github.com/Pylons/pyramid/pull/3457

- Avoid configuring logging in the monitor process using the logging config
  intended for the application. This avoids opening files for writing in both
  processes which can cause issues on some systems.
  See https://github.com/Pylons/pyramid/pull/3460

.. _changes_1.10.1:

1.10.1 (2018-11-06)
===================

- Fix an issue when passing a duck-typed registry object into
  ``pyramid.testing.setUp(registry=...)`` in which the registry wasn't
  properly fixed prior to invoking actions.
  See https://github.com/Pylons/pyramid/pull/3418

1.10 (2018-10-31)
=================

- No major changes from 1.10b1.

1.10b1 (2018-10-28)
===================

- Fix the ``pyramid.testing.DummyRequest`` to support the new
  ``request.accept`` API so that ``acceptable_offers`` is available even
  when code sets the value to a string.
  See https://github.com/Pylons/pyramid/pull/3396

- Fix deprecated escape sequences in preparation for Python 3.8.
  See https://github.com/Pylons/pyramid/pull/3400

1.10a1 (2018-10-15)
===================

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

- In ``cherrypy_server_runner``, prefer imports from the ``cheroot`` package
  over the legacy imports from `cherrypy.wsgiserver`.
  See https://github.com/Pylons/pyramid/pull/3235

- Add a context manager ``route_prefix_context`` to the
  ``pyramid.config.Configurator`` to allow for convenient setting of the
  route_prefix for ``include`` and ``add_route`` calls inside the context.
  See https://github.com/Pylons/pyramid/pull/3279

- Modify the builtin session implementations to support ``SameSite`` options
  on cookies and set the default to ``'Lax'``. This affects
  ``pyramid.session.BaseCookieSessionFactory``,
  ``pyramid.session.SignedCookieSessionFactory``, and
  ``pyramid.session.UnencryptedCookieSessionFactoryConfig``.
  See https://github.com/Pylons/pyramid/pull/3300

- Modify ``pyramid.authentication.AuthTktAuthenticationPolicy`` and
  ``pyramid.csrf.CookieCSRFStoragePolicy`` to support the ``SameSite`` option
  on cookies and set the default to ``'Lax'``.
  See https://github.com/Pylons/pyramid/pull/3319

- Added new ``pyramid.httpexceptions.HTTPPermanentRedirect``
  exception/response object for a HTTP 308 redirect.
  See https://github.com/Pylons/pyramid/pull/3302

- Within ``pshell``, allow the user-defined ``setup`` function to be a
  generator, in which case it may wrap the command's lifecycle.
  See https://github.com/Pylons/pyramid/pull/3318

- Within ``pshell``, variables defined by the ``[pshell]`` settings are
  available within the user-defined ``setup`` function.
  See https://github.com/Pylons/pyramid/pull/3318

- Add support for Python 3.7. Add testing on Python 3.8 with allowed failures.
  See https://github.com/Pylons/pyramid/pull/3333

- Added the ``pyramid.config.Configurator.add_accept_view_order`` directive,
  allowing users to specify media type preferences in ambiguous situations
  such as when several views match. A default ordering is defined for media
  types that prefers human-readable html/text responses over JSON.
  See https://github.com/Pylons/pyramid/pull/3326

- Support a list of media types in the ``accept`` predicate used in
  ``pyramid.config.Configurator.add_route``.
  See https://github.com/Pylons/pyramid/pull/3326

- Added ``pyramid.session.JSONSerializer``. See "Upcoming Changes to ISession
  in Pyramid 2.0" in the "Sessions" chapter of the documentation for more
  information about this feature.
  See https://github.com/Pylons/pyramid/pull/3353

- Add a ``registry`` argument to ``pyramid.renderers.get_renderer``
  to allow users to avoid threadlocals during renderer lookup.
  See https://github.com/Pylons/pyramid/pull/3358

- Pyramid's test suite is no longer distributed with the universal wheel.
  See https://github.com/Pylons/pyramid/pull/3387

- All Python code is now formatted automatically using ``black``.
  See https://github.com/Pylons/pyramid/pull/3388

Bug Fixes
---------

- Set appropriate ``code`` and ``title`` attributes on the ``HTTPClientError``
  and ``HTTPServerError`` exception classes. This prevents inadvertently
  returning a 520 error code.
  See https://github.com/Pylons/pyramid/pull/3280

- Replace ``webob.acceptparse.MIMEAccept`` from WebOb with
  ``webob.acceptparse.create_accept_header`` in the HTTP exception handling
  code. The old ``MIMEAccept`` has been deprecated. The new methods follow the
  RFC's more closely. See https://github.com/Pylons/pyramid/pull/3251

- Catch extra errors like ``AttributeError`` when unpickling "trusted"
  session cookies with bad pickle data in them. This would occur when sharing
  a secret between projects that shouldn't actually share session cookies,
  like when reusing secrets between projects in development.
  See https://github.com/Pylons/pyramid/pull/3325

Deprecations
------------

- The ``pyramid.intefaces.ISession`` interface will move to require
  JSON-serializable objects in Pyramid 2.0. See
  "Upcoming Changes to ISession in Pyramid 2.0" in the "Sessions" chapter
  of the documentation for more information about this change.
  See https://github.com/Pylons/pyramid/pull/3353

- The ``pyramid.session.signed_serialize`` and
  ``pyramid.session.signed_deserialize`` functions will be removed in Pyramid
  2.0, along with the removal of
  ``pyramid.session.UnencryptedCookieSessionFactoryConfig`` which was
  deprecated in Pyramid 1.5. Please switch to using the
  ``SignedCookieSessionFactory``, copying the code, or another session
  implementation if you're still using these features.
  See https://github.com/Pylons/pyramid/pull/3353

- Media ranges are deprecated in the ``accept`` argument of
  ``pyramid.config.Configurator.add_route``. Use a list of explicit
  media types to ``add_route`` to support multiple types.

- Media ranges are deprecated in the ``accept`` argument of
  ``pyramid.config.Configurator.add_view``.  There is no replacement for
  ranges to ``add_view``, but after much discussion the workflow is
  fundamentally ambiguous in the face of various client-supplied values for
  the ``Accept`` header.
  See https://github.com/Pylons/pyramid/pull/3326

Backward Incompatibilities
--------------------------

- On Python 3.4+ the ``repoze.lru`` dependency is dropped. If you were using
  this package directly in your apps you should make sure that you are
  depending on it directly within your project.
  See https://github.com/Pylons/pyramid/pull/3140

- Remove the ``permission`` argument from
  ``pyramid.config.Configurator.add_route``. This was an argument left over
  from a feature removed in Pyramid 1.5 and has had no effect since then.
  See https://github.com/Pylons/pyramid/pull/3299

- Modify the builtin session implementations to set ``SameSite='Lax'`` on
  cookies. This affects ``pyramid.session.BaseCookieSessionFactory``,
  ``pyramid.session.SignedCookieSessionFactory``, and
  ``pyramid.session.UnencryptedCookieSessionFactoryConfig``.
  See https://github.com/Pylons/pyramid/pull/3300

- Variables defined in the ``[pshell]`` section of the settings will no
  longer override those set by the ``setup`` function.
  See https://github.com/Pylons/pyramid/pull/3318

- ``pyramid.config.Configurator.add_notfound_view`` uses default redirect
  class exception ``pyramid.httpexceptions.HTTPTemporaryRedirect`` instead
  of previous ``pyramid.httpexceptions.HTTPFound``.
  See https://github.com/Pylons/pyramid/pull/3328

- Removed ``pyramid.config.Configurator.set_request_property`` which had been
  deprecated since Pyramid 1.5. Instead use
  ``pyramid.config.Configurator.add_request_method`` with ``reify=True`` or
  ``property=True``.
  See https://github.com/Pylons/pyramid/pull/3368

- Removed the ``principal`` keyword argument from
  ``pyramid.security.remember`` which had been deprecated since Pyramid 1.6
  and replaced by the ``userid`` argument.
  See https://github.com/Pylons/pyramid/pull/3369

- Removed the ``pyramid.tests`` subpackage that used to contain the Pyramid
  test suite. These changes also changed the format of the repository to move
  the code into a ``src`` folder.
  See https://github.com/Pylons/pyramid/pull/3387

Documentation Changes
---------------------

- Ad support for Read The Docs Ethical Ads.
  See https://github.com/Pylons/pyramid/pull/3360 and
  https://docs.readthedocs.io/en/latest/advertising/ethical-advertising.html

- Add support for alembic to the pyramid-cookiecutter-alchemy cookiecutter
  and update the wiki2 tutorial to explain how it works.
  See https://github.com/Pylons/pyramid/pull/3307 and
  https://github.com/Pylons/pyramid-cookiecutter-alchemy/pull/7

- Bump Sphinx to >= 1.7.4 in setup.py to support ``emphasize-lines`` in PDFs
  and to pave the way for xelatex support.  See
  https://github.com/Pylons/pyramid/pull/3271,
  https://github.com/Pylons/pyramid/issues/667, and
  https://github.com/Pylons/pyramid/issues/2572

- Added extra tests to the quick tutorial.
  See https://github.com/Pylons/pyramid/pull/3375
