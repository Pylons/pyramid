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
  ``pyramid.csrf.CookieCSRFStoragePolicy`` to support the SameSite option on
  cookies and set the default to ``'Lax'``.
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

- Added ``pyramid.session.JSONSerializer``. See "Upcoming Changes to ISession
  in Pyramid 2.0" in the "Sessions" chapter of the documentation for more
  information about this feature.
  See https://github.com/Pylons/pyramid/pull/3353

- Add a ``registry`` argument to ``pyramid.renderers.get_renderer``
  to allow users to avoid threadlocals during renderer lookup.
  See https://github.com/Pylons/pyramid/pull/3358

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

Documentation Changes
---------------------

- Ad support for Read The Docs Ethical Ads.
  https://github.com/Pylons/pyramid/pull/3360
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
