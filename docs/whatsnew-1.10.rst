What's New in Pyramid 1.10
==========================

This article explains the new features in :app:`Pyramid` version 1.10 as compared to its predecessor, :app:`Pyramid` 1.9. It also documents backwards incompatibilities between the two versions and deprecations added to :app:`Pyramid` 1.10, as well as software dependency changes and notable documentation additions.

.. note::

    This release is the last planned feature release to support Python 2.7.
    Bug fixes will continue to be backported until at least 2020-01-01 when Python 2.7 reaches end of life.
    New features and backports will be reviewed and accepted for the 1.x series of Pyramid but new development will be focused on Pyramid 2.x.

Bug Fix Releases
----------------

Pyramid 1.10 was released on 2018-10-31.

The following bug fix releases were made since then. Bug fix releases also include documentation improvements and other minor feature changes.

- :ref:`changes_1.10.1`
- :ref:`changes_1.10.2`

Feature Additions
-----------------

- Add support for Python 3.7. Add testing on Python 3.8 with allowed failures.
  See https://github.com/Pylons/pyramid/pull/3333

- Add a context manager :meth:`pyramid.config.Configurator.route_prefix_context` to allow for convenient setting of the ``route_prefix`` for :meth:`pyramid.config.Configurator.include` and :meth:`pyramid.config.Configurator.add_route` calls inside the context.
  See https://github.com/Pylons/pyramid/pull/3279

- Added the :meth:`pyramid.config.Configurator.add_accept_view_order` directive, allowing users to specify media type preferences in ambiguous situations such as when several views match.
  A default ordering is defined for media types that prefers human-readable html/text responses over JSON.
  See https://github.com/Pylons/pyramid/pull/3326

- Support a list of media types in the ``accept`` predicate used in :meth:`pyramid.config.Configurator.add_route`.
  See https://github.com/Pylons/pyramid/pull/3326

- Added :class:`pyramid.session.JSONSerializer`.
  See :ref:`pickle_session_deprecation` for more information about this feature.
  See https://github.com/Pylons/pyramid/pull/3353

- Modify the builtin session implementations to support ``SameSite`` options on cookies and set the default to ``'Lax'``.
  This affects :func:`pyramid.session.BaseCookieSessionFactory`, :func:`pyramid.session.SignedCookieSessionFactory`, and :func:`pyramid.session.UnencryptedCookieSessionFactoryConfig`.
  See https://github.com/Pylons/pyramid/pull/3300

- Modify :class:`pyramid.authentication.AuthTktAuthenticationPolicy` and :class:`pyramid.csrf.CookieCSRFStoragePolicy` to support the ``SameSite`` option on cookies and set the default to ``'Lax'``.
  See https://github.com/Pylons/pyramid/pull/3319

- Added new :class:`pyramid.httpexceptions.HTTPPermanentRedirect` exception/response object for a HTTP 308 redirect.
  See https://github.com/Pylons/pyramid/pull/3302

- Add ``_depth`` and ``_category`` arguments to all of the venusian decorators.
  The ``_category`` argument can be used to affect which actions are registered when performing a ``config.scan(..., category=...)`` with a specific category.
  The ``_depth`` argument should be used when wrapping the decorator in your own.
  This change affects :func:`pyramid.view.view_config`, :func:`pyramid.view.exception_view_config`, :func:`pyramid.view.forbidden_view_config`, :func:`pyramid.view.notfound_view_config`, :func:`pyramid.events.subscriber` and :func:`pyramid.response.response_adapter` decorators.
  See https://github.com/Pylons/pyramid/pull/3105 and https://github.com/Pylons/pyramid/pull/3122

- Fix the :class:`pyramid.request.Request` class name after using :meth:`pyramid.request.Request.set_property` or :meth:`pyramid.config.Configurator.add_request_method` such that the ``str(request.__class__)`` would appear as ``pyramid.request.Request`` instead of ``pyramid.util.Request``.
  See https://github.com/Pylons/pyramid/pull/3129

- Add a ``registry`` argument to :func:`pyramid.renderers.get_renderer` to allow users to avoid threadlocals during renderer lookup.
  See https://github.com/Pylons/pyramid/pull/3358

- Within ``pshell``, allow the user-defined ``setup`` function to be a generator, in which case it may wrap the command's lifecycle.
  See https://github.com/Pylons/pyramid/pull/3318

- Within ``pshell``, variables defined by the ``[pshell]`` settings are available within the user-defined ``setup`` function.
  See https://github.com/Pylons/pyramid/pull/3318

- In ``cherrypy_server_runner``, prefer imports from the ``cheroot`` package over the legacy imports from `cherrypy.wsgiserver`.
  See https://github.com/Pylons/pyramid/pull/3235

- :app:`Pyramid`'s test suite is no longer distributed with the universal wheel.
  See https://github.com/Pylons/pyramid/pull/3387

- All Python code is now formatted automatically using ``black``.
  See https://github.com/Pylons/pyramid/pull/3388

Deprecations
------------

- The :class:`pyramid.interfaces.ISession` interface will move to require JSON-serializable objects in :app:`Pyramid` 2.0. See :ref:`pickle_session_deprecation` for more information about this change.
  See https://github.com/Pylons/pyramid/pull/3353

- The :func:`pyramid.session.signed_serialize` and :func:`pyramid.session.signed_deserialize` functions will be removed in :app:`Pyramid` 2.0, along with the removal of :func:`pyramid.session.UnencryptedCookieSessionFactoryConfig` which was deprecated in :app:`Pyramid` 1.5.
  Please switch to using the :func:`pyramid.session.SignedCookieSessionFactory`, copying the code, or another session implementation if you're still using these features.
  See https://github.com/Pylons/pyramid/pull/3353

- Media ranges are deprecated in the ``accept`` argument of :meth:`pyramid.config.Configurator.add_route`.
  Use a list of explicit media types to ``add_route`` to support multiple types.
  See https://github.com/Pylons/pyramid/pull/3326

- Media ranges are deprecated in the ``accept`` argument of :meth:`pyramid.config.Configurator.add_view`.
  There is no replacement for ranges to ``add_view``, but after much discussion the workflow is fundamentally ambiguous in the face of various client-supplied values for the ``Accept`` header.
  See https://github.com/Pylons/pyramid/pull/3326

Backward Incompatibilities
--------------------------

- Removed ``pyramid.config.Configurator.set_request_property`` which had been deprecated since :app:`Pyramid` 1.5.
  Instead use :meth:`pyramid.config.Configurator.add_request_method` with ``reify=True`` or ``property=True``.
  See https://github.com/Pylons/pyramid/pull/3368

- On Python 3.4+ the ``repoze.lru`` dependency is dropped.
  If you were using this package directly in your apps you should make sure that you are depending on it directly within your project.
  See https://github.com/Pylons/pyramid/pull/3140

- Remove the ``permission`` argument from :meth:`pyramid.config.Configurator.add_route`.
  This was an argument left over from a feature removed in :app:`Pyramid` 1.5 and has had no effect since then.
  See https://github.com/Pylons/pyramid/pull/3299

- Modified the builtin session implementations to set ``SameSite='Lax'`` on cookies.
  This affects :func:`pyramid.session.BaseCookieSessionFactory`, :func:`pyramid.session.SignedCookieSessionFactory`, and :func:`pyramid.session.UnencryptedCookieSessionFactoryConfig`.
  See https://github.com/Pylons/pyramid/pull/3300

- Variables defined in the ``[pshell]`` section of the settings will no longer override those set by the ``setup`` function.
  See https://github.com/Pylons/pyramid/pull/3318

- :meth:`pyramid.config.Configurator.add_notfound_view` uses default redirect class exception :class:`pyramid.httpexceptions.HTTPTemporaryRedirect` instead of previous :class:`pyramid.httpexceptions.HTTPFound`.
  See https://github.com/Pylons/pyramid/pull/3328

- Removed the ``principal`` keyword argument from :func:`pyramid.security.remember` which had been deprecated since :app:`Pyramid` 1.6 and replaced by the ``userid`` argument.
  See https://github.com/Pylons/pyramid/pull/3369

- Removed the ``pyramid.tests`` subpackage that used to contain the Pyramid test suite.
  These changes also changed the format of the repository to move the code into a ``src`` folder.
  See https://github.com/Pylons/pyramid/pull/3387

Documentation Enhancements
--------------------------

- Ad support for Read The Docs Ethical Ads.
  See https://github.com/Pylons/pyramid/pull/3360 and https://docs.readthedocs.io/en/latest/advertising/ethical-advertising.html

- Add support for alembic to the pyramid-cookiecutter-alchemy cookiecutter and update the wiki2 tutorial to explain how it works.
  See https://github.com/Pylons/pyramid/pull/3307 and https://github.com/Pylons/pyramid-cookiecutter-alchemy/pull/7

- Bump Sphinx to >= 1.7.4 in setup.py to support ``emphasize-lines`` in PDFs and to pave the way for xelatex support.
  See https://github.com/Pylons/pyramid/pull/3271, https://github.com/Pylons/pyramid/issues/667, and https://github.com/Pylons/pyramid/issues/2572

- Added extra tests to the quick tutorial.
  See https://github.com/Pylons/pyramid/pull/3375
