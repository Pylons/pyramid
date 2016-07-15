What's New in Pyramid 1.7
=========================

This article explains the new features in :app:`Pyramid` version 1.7 as
compared to its predecessor, :app:`Pyramid` 1.6. It also documents backwards
incompatibilities between the two versions and deprecations added to
:app:`Pyramid` 1.7, as well as software dependency changes and notable
documentation additions.

Backwards Incompatibilities
---------------------------

- The default hash algorithm for
  :class:`pyramid.authentication.AuthTktAuthenticationPolicy` has changed from
  ``md5`` to ``sha512``. If you are using the authentication policy and need to
  continue using ``md5``, please explicitly set ``hashalg='md5'``.

  If you are not currently specifying the ``hashalg`` option in your apps, then
  this change means any existing auth tickets (and associated cookies) will no
  longer be valid, users will be logged out, and have to login to their
  accounts again.

  This change has been issuing a DeprecationWarning since :app:`Pyramid` 1.4.

  See https://github.com/Pylons/pyramid/pull/2496

- Python 2.6 and 3.2 are no longer supported by Pyramid. See
  https://github.com/Pylons/pyramid/issues/2368 and
  https://github.com/Pylons/pyramid/pull/2256

- The :func:`pyramid.session.check_csrf_token` function no longer validates a
  csrf token in the query string of a request. Only headers and request bodies
  are supported. See https://github.com/Pylons/pyramid/pull/2500

- A global permission set via
  :meth:`pyramid.config.Configurator.set_default_permission` will no longer
  affect exception views. A permission must be set explicitly on the view for
  it to be enforced. See https://github.com/Pylons/pyramid/pull/2534

Feature Additions
-----------------

- A new :ref:`view_derivers` concept has been added to Pyramid to allow
  framework authors to inject elements into the standard Pyramid view pipeline
  and affect all views in an application. This is similar to a decorator except
  that it has access to options passed to ``config.add_view`` and can affect
  other stages of the pipeline such as the raw response from a view or prior
  to security checks. See https://github.com/Pylons/pyramid/pull/2021

- Added a ``require_csrf`` view option which will enforce CSRF checks on
  requests with an unsafe method as defined by RFC2616. If the CSRF check fails
  a ``BadCSRFToken`` exception will be raised and may be caught by exception
  views (the default response is a ``400 Bad Request``). This option should be
  used in place of the deprecated ``check_csrf`` view predicate which would
  normally result in unexpected ``404 Not Found`` response to the client
  instead of a catchable exception.  See :ref:`auto_csrf_checking`,
  https://github.com/Pylons/pyramid/pull/2413 and
  https://github.com/Pylons/pyramid/pull/2500

- Added a new method,
  :meth:`pyramid.config.Configurator.set_csrf_default_options`,
  for configuring CSRF checks used by the ``require_csrf=True`` view option.
  This method can be used to turn on CSRF checks globally for every view
  in the application. This should be considered a good default for websites
  built on Pyramid. It is possible to opt-out of CSRF checks on a per-view
  basis by setting ``require_csrf=False`` on those views.
  See :ref:`auto_csrf_checking` and
  https://github.com/Pylons/pyramid/pull/2413 and
  https://github.com/Pylons/pyramid/pull/2518

- Added an additional CSRF validation that checks the origin/referrer of a
  request and makes sure it matches the current ``request.domain``. This
  particular check is only active when accessing a site over HTTPS as otherwise
  browsers don't always send the required information. If this additional CSRF
  validation fails a ``BadCSRFOrigin`` exception will be raised and may be
  caught by exception views (the default response is ``400 Bad Request``).
  Additional allowed origins may be configured by setting
  ``pyramid.csrf_trusted_origins`` to a list of domain names (with ports if on
  a non standard port) to allow. Subdomains are not allowed unless the domain
  name has been prefixed with a ``.``. See
  https://github.com/Pylons/pyramid/pull/2501

- Added a new :func:`pyramid.session.check_csrf_origin` API for validating the
  origin or referrer headers against the request's domain.
  See https://github.com/Pylons/pyramid/pull/2501

- Subclasses of :class:`pyramid.httpexceptions.HTTPException` will now take
  into account the best match for the clients ``Accept`` header, and depending
  on what is requested will return ``text/html``, ``application/json`` or
  ``text/plain``. The default for ``*/*`` is still ``text/html``, but if
  ``application/json`` is explicitly mentioned it will now receive a valid
  JSON response. See https://github.com/Pylons/pyramid/pull/2489

- A new event, :class:`pyramid.events.BeforeTraversal`, and interface
  :class:`pyramid.interfaces.IBeforeTraversal` have been introduced that will
  notify listeners before traversal starts in the router.
  See :ref:`router_chapter` as well as
  https://github.com/Pylons/pyramid/pull/2469 and
  https://github.com/Pylons/pyramid/pull/1876

- A new method, :meth:`pyramid.request.Request.invoke_exception_view`, which
  can be used to invoke an exception view and get back a response. This is
  useful for rendering an exception view outside of the context of the
  ``EXCVIEW`` tween where you may need more control over the request.
  See https://github.com/Pylons/pyramid/pull/2393

- A global permission set via
  :meth:`pyramid.config.Configurator.set_default_permission` will no longer
  affect exception views. A permission must be set explicitly on the view for
  it to be enforced. See https://github.com/Pylons/pyramid/pull/2534

- Allow a leading ``=`` on the key of the request param predicate.
  For example, ``'=abc=1'`` is equivalent down to
  ``request.params['=abc'] == '1'``.
  See https://github.com/Pylons/pyramid/pull/1370

- Allow using variable substitutions like ``%(LOGGING_LOGGER_ROOT_LEVEL)s``
  for logging sections of the .ini file and populate these variables from
  the ``pserve`` command line -- e.g.:

  ``pserve development.ini LOGGING_LOGGER_ROOT_LEVEL=DEBUG``

  This support is thanks to the new ``global_conf`` option on
  :func:`pyramid.paster.setup_logging`.
  See https://github.com/Pylons/pyramid/pull/2399

- The :attr:`pyramid.tweens.EXCVIEW` tween will now re-raise the original
  exception if no exception view could be found to handle it. This allows
  the exception to be handled upstream by another tween or middelware.
  See https://github.com/Pylons/pyramid/pull/2567

Deprecations
------------

- The ``check_csrf`` view predicate has been deprecated. Use the
  new ``require_csrf`` option or the ``pyramid.require_default_csrf`` setting
  to ensure that the :class:`pyramid.exceptions.BadCSRFToken` exception is
  raised. See https://github.com/Pylons/pyramid/pull/2413

- Support for Python 3.3 will be removed in Pyramid 1.8.
  https://github.com/Pylons/pyramid/issues/2477

Scaffolding Enhancements
------------------------

- A complete overhaul of the ``alchemy`` scaffold to show more modern best
  practices with regards to SQLAlchemy session management, as well as a more
  modular approach to configuration, separating routes into a separate module
  to illustrate uses of :meth:`pyramid.config.Configurator.include`.
  See https://github.com/Pylons/pyramid/pull/2024

Documentation Enhancements
--------------------------

A massive overhaul of the packaging and tools used in the documentation
was completed in https://github.com/Pylons/pyramid/pull/2468. A summary
follows:

- All docs now recommend using ``pip`` instead of ``easy_install``.

- The installation docs now expect the user to be using Python 3.4 or
  greater with access to the ``python3 -m venv`` tool to create virtual
  environments.

- Tutorials now use ``py.test`` and ``pytest-cov`` instead of ``nose`` and
  ``coverage``.

- Further updates to the scaffolds as well as tutorials and their src files.

Along with the overhaul of the ``alchemy`` scaffold came a total overhaul
of the :ref:`bfg_sql_wiki_tutorial` tutorial to introduce more modern
features into the usage of SQLAlchemy with Pyramid and provide a better
starting point for new projects. See
https://github.com/Pylons/pyramid/pull/2024 for more. Highlights were:

- New SQLAlchemy session management without any global ``DBSession``. Replaced
  by a per-request ``request.dbsession`` property.

- A new authentication chapter demonstrating how to get simple authentication
  bootstrapped quickly in an application.

- Authorization was overhauled to show the use of per-route context factories
  which demonstrate object-level authorization on top of simple group-level
  authorization. Did you want to restrict page edits to only the owner but
  couldn't figure it out before? Here you go!

- The users and groups are stored in the database now instead of within
  tutorial-specific global variables.

- User passwords are stored using ``bcrypt``.
