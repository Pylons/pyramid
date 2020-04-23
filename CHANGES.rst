unreleased
==========

Features
--------

- It is now possible to pass multiple values to the ``header`` predicate
  for route and view configuration.
  See https://github.com/Pylons/pyramid/pull/3576

- Add support for Python 3.8.
  See https://github.com/Pylons/pyramid/pull/3547

- New security APIs have been added to support a massive overhaul of the
  authentication and authorization system. Read
  "Upgrading Authentication/Authorization" in the "What's New in Pyramid 2.0"
  document for information about using this new system.

  - ``pyramid.config.Configurator.set_security_policy``.
  - ``pyramid.interfaces.ISecurityPolicy``
  - ``pyramid.request.Request.authenticated_identity``.
  - ``pyramid.authentication.SessionAuthenticationHelper``
  - ``pyramid.authorization.ACLHelper``

  See https://github.com/Pylons/pyramid/pull/3465

- Changed the default ``serializer`` on
  ``pyramid.session.SignedCookieSessionFactory`` to use
  ``pyramid.session.JSONSerializer`` instead of
  ``pyramid.session.PickleSerializer``. Read
  "Changes to ISession in Pyramid 2.0" in the "Sessions" chapter of the
  documentation for more information about why this change was made.
  See https://github.com/Pylons/pyramid/pull/3413

- It is now possible to control whether a route pattern contains a trailing
  slash when it is composed with a route prefix using
  ``config.include(..., route_prefix=...)`` or
  ``with config.route_prefix_context(...)``. This can be done by specifying
  an empty pattern and setting the new argument
  ``inherit_slash=True``. For example:

  .. code-block:: python

      with config.route_prefix_context('/users'):
          config.add_route('users', '', inherit_slash=True)

  In the example, the resulting pattern will be ``/users``. Similarly, if the
  route prefix were ``/users/`` then the final pattern would be ``/users/``.
  If the ``pattern`` was ``'/'``, then the final pattern would always be
  ``/users/``. This new setting is only available if the pattern supplied
  to ``add_route`` is the empty string (``''``).
  See https://github.com/Pylons/pyramid/pull/3420

- No longer define ``pyramid.request.Request.json_body`` which is already
  provided by WebOb. This allows the attribute to now be settable.
  See https://github.com/Pylons/pyramid/pull/3447

- Improve debugging info from ``pyramid.view.view_config`` decorator.
  See https://github.com/Pylons/pyramid/pull/3483

- A new parameter, ``allow_no_origin``, was added to
  ``pyramid.config.Configurator.set_default_csrf_options`` as well as
  ``pyramid.csrf.check_csrf_origin``. This option controls whether a
  request is rejected if it has no ``Origin`` or ``Referer`` header -
  often the result of a user configuring their browser not to send a
  ``Referer`` header for privacy reasons even on same-domain requests.
  The default is to reject requests without a known origin. It is also
  possible to allow the special ``Origin: null`` header by adding it to the
  ``pyramid.csrf_trusted_origins`` list in the settings.
  See https://github.com/Pylons/pyramid/pull/3512
  and https://github.com/Pylons/pyramid/pull/3518

- A new parameter, ``check_origin``, was added to
  ``pyramid.config.Configurator.set_default_csrf_options`` which disables
  origin checking entirely.
  See https://github.com/Pylons/pyramid/pull/3518

- Added ``pyramid.interfaces.IPredicateInfo`` which defines the object passed
  to predicate factories as their second argument.
  See https://github.com/Pylons/pyramid/pull/3514

- Added support for serving pre-compressed static assets by using the
  ``content_encodings`` argument of
  ``pyramid.config.Configurator.add_static_view`` and
  ``pyramid.static.static_view``.
  See https://github.com/Pylons/pyramid/pull/3537

- Fix ``DeprecationWarning`` emitted by using the ``imp`` module.
  See https://github.com/Pylons/pyramid/pull/3553

- Properties created via ``config.add_request_method(..., property=True)`` or
  ``request.set_property`` used to be readonly. They can now be overridden
  via ``request.foo = ...`` and until the value is deleted it will return
  the overridden value. This is most useful when mocking request properties
  in testing.
  See https://github.com/Pylons/pyramid/pull/3559

- Finished callbacks are now executed as part of the ``closer`` that is
  invoked as part of ``pyramid.scripting.prepare`` and
  ``pyramid.paster.bootstrap``.
  See https://github.com/Pylons/pyramid/pull/3561

- Added ``pyramid.request.RequestLocalCache`` which can be used to create
  simple objects that are shared across requests and can be used to store
  per-request data. This is useful when the source of data is external to
  the request itself. Often a reified property is used on a request via
  ``pyramid.config.Configurator.add_request_method``, or
  ``pyramid.decorator.reify``, and these work great when the data is
  generated on-demand when accessing the request property. However, often
  the case is that the data is generated when accessing some other system
  and then we want to cache the data for the duration of the request.
  See https://github.com/Pylons/pyramid/pull/3561

- Exposed ``pyramid.authorization.ALL_PERMISSIONS`` and
  ``pyramid.authorization.DENY_ALL`` such that all of the ACL-related constants
  are now importable from the ``pyramid.authorization`` namespace.
  See https://github.com/Pylons/pyramid/pull/3563

Deprecations
------------

- Deprecated the authentication and authorization interfaces and
  principal-based support. See "Upgrading Authentication/Authorization" in
  the "What's New in Pyramid 2.0" document for information on equivalent APIs
  and notes on upgrading. The following APIs are deprecated as a result of
  this change:

  - ``pyramid.config.Configurator.set_authentication_policy``
  - ``pyramid.config.Configurator.set_authorization_policy``
  - ``pyramid.interfaces.IAuthenticationPolicy``
  - ``pyramid.interfaces.IAuthorizationPolicy``
  - ``pyramid.request.Request.effective_principals``
  - ``pyramid.request.Request.unauthenticated_userid``
  - ``pyramid.authentication.AuthTktAuthenticationPolicy``
  - ``pyramid.authentication.RemoteUserAuthenticationPolicy``
  - ``pyramid.authentication.RepozeWho1AuthenticationPolicy``
  - ``pyramid.authentication.SessionAuthenticationPolicy``
  - ``pyramid.authentication.BasicAuthAuthenticationPolicy``
  - ``pyramid.authorization.ACLAuthorizationPolicy``
  - The ``effective_principals`` view and route predicates.

  See https://github.com/Pylons/pyramid/pull/3465

- Deprecated ``pyramid.security.principals_allowed_by_permission``. This
  method continues to work with the deprecated
  ``pyramid.interfaces.IAuthorizationPolicy`` interface but will not work with
  the new ``pyramid.interfaces.ISecurityPolicy``.
  See https://github.com/Pylons/pyramid/pull/3465

- Deprecated several ACL-related aspects of ``pyramid.security``. Equivalent
  objects should now be imported from the ``pyramid.authorization`` namespace.
  This includes:

  - ``pyramid.security.Everyone``
  - ``pyramid.security.Authenticated``
  - ``pyramid.security.ALL_PERMISSIONS``
  - ``pyramid.security.DENY_ALL``
  - ``pyramid.security.ACLAllowed``
  - ``pyramid.security.ACLDenied``

  See https://github.com/Pylons/pyramid/pull/3563

- Deprecated ``pyramid.session.PickleSerializer``.
  See https://github.com/pylons/pyramid/issues/2709
  and https://github.com/pylons/pyramid/pull/3353
  and https://github.com/pylons/pyramid/pull/3413

Backward Incompatibilities
--------------------------

- Drop support for Python 2.7.
  https://github.com/Pylons/pyramid/pull/3421

- Drop support for Python 3.4.
  See https://github.com/Pylons/pyramid/pull/3547

- Removed the ``pyramid.compat`` module. Integrators should use the ``six``
  module or vendor shims they are using into their own codebases going forward.
  https://github.com/Pylons/pyramid/pull/3421

- ``pcreate`` and the builtin scaffolds have been removed in favor of
  using the ``cookiecutter`` tool and the ``pyramid-cookiecutter-starter``
  cookiecutter. The script and scaffolds were deprecated in Pyramid 1.8.
  See https://github.com/Pylons/pyramid/pull/3406

- Changed the default ``hashalg`` on
  ``pyramid.authentication.AuthTktCookieHelper`` to ``sha512``.
  See https://github.com/Pylons/pyramid/pull/3557

- Removed ``pyramid.interfaces.ITemplateRenderer``. This interface was
  deprecated since Pyramid 1.5 and was an interface
  used by libraries like ``pyramid_mako`` and ``pyramid_chameleon`` but
  provided no functionality within Pyramid itself.
  See https://github.com/Pylons/pyramid/pull/3409

- Removed ``pyramid.security.has_permission``,
  ``pyramid.security.authenticated_userid``,
  ``pyramid.security.unauthenticated_userid``, and
  ``pyramid.security.effective_principals``. These methods were deprecated
  in Pyramid 1.5 and all have equivalents available as properties on the
  request. For example, ``request.authenticated_userid``.
  See https://github.com/Pylons/pyramid/pull/3410

- Removed support for supplying a media range to the ``accept`` predicate of
  both ``pyramid.config.Configurator.add_view`` and
  ``pyramid.config.Configurator.add_route``. These options were deprecated
  in Pyramid 1.10 and WebOb 1.8 because they resulted in uncontrollable
  matching that was not compliant with the RFC.
  See https://github.com/Pylons/pyramid/pull/3411

- Removed ``pyramid.session.UnencryptedCookieSessionFactoryConfig``. This
  session factory was replaced with
  ``pyramid.session.SignedCookieSessionFactory`` in Pyramid 1.5 and has been
  deprecated since then.
  See https://github.com/Pylons/pyramid/pull/3412

- Removed ``pyramid.session.signed_serialize``, and
  ``pyramid.session.signed_deserialize``. These methods were only used by
  the now-removed ``pyramid.session.UnencryptedCookieSessionFactoryConfig``
  and were coupled to the vulnerable pickle serialization format which could
  lead to remove code execution if the secret key is compromised.
  See https://github.com/Pylons/pyramid/pull/3412

- Changed the default ``serializer`` on
  ``pyramid.session.SignedCookieSessionFactory`` to use
  ``pyramid.session.JSONSerializer`` instead of
  ``pyramid.session.PickleSerializer``. Read
  "Changes to ISession in Pyramid 2.0" in the "Sessions" chapter of the
  documentation for more information about why this change was made.
  See https://github.com/Pylons/pyramid/pull/3413

- ``pyramid.request.Request.invoke_exception_view`` will no longer be called
  by the default execution policy.
  See https://github.com/Pylons/pyramid/pull/3496

- ``pyramid.config.Configurator.scan`` will no longer, by default, execute
  Venusian decorator callbacks registered for categories other than
  ``'pyramid'``. To find any decorator regardless of category, specify
  ``config.scan(..., categories=None)``.
  See https://github.com/Pylons/pyramid/pull/3510

- The second argument to predicate factories has been changed from ``config``
  to ``info``, an instance of ``pyramid.interfaces.IPredicateInfo``. This
  limits the data available to predicates but still provides the package,
  registry, settings and dotted-name resolver which should cover most use
  cases and is largely backward compatible.
  See https://github.com/Pylons/pyramid/pull/3514

- Removed the ``check_csrf`` predicate. Instead, use
  ``pyramid.config.Configurator.set_default_csrf_options`` and the
  ``require_csrf`` view option to enable automatic CSRF checking.
  See https://github.com/Pylons/pyramid/pull/3521

Documentation Changes
---------------------

- Restore build of PDF on Read The Docs.
  See https://github.com/Pylons/pyramid/issues/3290

- Fix docs build for Sphinx 2.0.
  See https://github.com/Pylons/pyramid/pull/3480

- Significant updates to the wiki, wiki2 tutorials to demonstrate the new
  security policy usage as well as a much more production-ready test harness.
  See https://github.com/Pylons/pyramid/pull/3557
