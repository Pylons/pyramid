What's New in Pyramid 2.0
=========================

This article explains the new features in :app:`Pyramid` version 2.0 as compared to its predecessor, :app:`Pyramid` 1.10.
It also documents backwards incompatibilities between the two versions and deprecations added to :app:`Pyramid` 2.0, as well as software dependency changes and notable documentation additions.

.. note::

    This is the first release of :app:`Pyramid` that does not support Python 2, which is now End-of-Life and no longer receiving critical security updates by the PSF.

Feature Additions
-----------------

The feature additions in Pyramid 2.0 are as follows:

- The authentication and authorization policies of Pyramid 1.x have been merged into a single :term:`security policy` in Pyramid 2.0.
  For details on how to migrate to the new security policy, see :ref:`upgrading_auth`.
  Authentication and authorization policies can still be used and will continue to function normally for the time being.

  New security APIs have been added to support an overhaul of the authentication and authorization system.
  Read :ref:`upgrading_auth` for information about using this new system.

  - :meth:`pyramid.config.Configurator.set_security_policy`
  - :class:`pyramid.interfaces.ISecurityPolicy`
  - :attr:`pyramid.request.Request.authenticated_identity`
  - :class:`pyramid.authentication.AuthTktCookieHelper` (available in Pyramid 1.x)
  - :class:`pyramid.authentication.SessionAuthenticationHelper`
  - :class:`pyramid.authorization.ACLHelper`

  See https://github.com/Pylons/pyramid/pull/3465

- Changed the default ``serializer`` on :class:`pyramid.session.SignedCookieSessionFactory` to use :class:`pyramid.session.JSONSerializer` instead of :class:`pyramid.session.PickleSerializer`.
  Read "Changes to ISession in Pyramid 2.0" in the "Sessions" chapter of the documentation for more information about why this change was made.
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

- A new parameter, ``allow_no_origin``, was added to :meth:`pyramid.config.Configurator.set_default_csrf_options` as well as :func:`pyramid.csrf.check_csrf_origin`.
  This option controls whether a request is rejected if it has no ``Origin`` or ``Referer`` header - often the result of a user configuring their browser not to send a ``Referer`` header for privacy reasons even on same-domain requests.
  The default is to reject requests without a known origin.
  It is also possible to allow the special ``Origin: null`` header by adding it to the ``pyramid.csrf_trusted_origins`` list in the settings.
  See https://github.com/Pylons/pyramid/pull/3512 and https://github.com/Pylons/pyramid/pull/3518

- A new parameter, ``check_origin``, was added to :meth:`pyramid.config.Configurator.set_default_csrf_options` which disables origin checking entirely.
  See https://github.com/Pylons/pyramid/pull/3518

- Added :class:`pyramid.interfaces.IPredicateInfo` which defines the object passed to predicate factories as their second argument.
  See https://github.com/Pylons/pyramid/pull/3514

- Added support for serving pre-compressed static assets by using the ``content_encodings`` argument of :meth:`pyramid.config.Configurator.add_static_view` and :func:`pyramid.static.static_view`.
  See https://github.com/Pylons/pyramid/pull/3537

- Fix ``DeprecationWarning`` emitted by using the ``imp`` module.
  See https://github.com/Pylons/pyramid/pull/3553

- Properties created via ``config.add_request_method(..., property=True)`` or ``request.set_property`` used to be readonly.
  They can now be overridden via ``request.foo = ...`` and until the value is deleted it will return the overridden value.
  This is most useful when mocking request properties in testing.
  See https://github.com/Pylons/pyramid/pull/3559

- Finished callbacks are now executed as part of the ``closer`` that is invoked as part of :func:`pyramid.scripting.prepare` and :func:`pyramid.paster.bootstrap`.
  See https://github.com/Pylons/pyramid/pull/3561

- Added :class:`pyramid.request.RequestLocalCache` which can be used to create simple objects that are shared across requests and can be used to store per-request data.
  This is useful when the source of data is external to the request itself.
  Often a reified property is used on a request via :meth:`pyramid.config.Configurator.add_request_method`, or :class:`pyramid.decorator.reify`.
  These work great when the data is generated on-demand when accessing the request property.
  However, often the case is that the data is generated when accessing some other system
  and then we want to cache the data for the duration of the request.
  See https://github.com/Pylons/pyramid/pull/3561

- Exposed :data:`pyramid.authorization.ALL_PERMISSIONS` and :data:`pyramid.authorization.DENY_ALL` such that all of the ACL-related constants are now importable from the ``pyramid.authorization`` namespace.
  See https://github.com/Pylons/pyramid/pull/3563

Deprecations
------------

- Authentication and authorization policies have been deprecated in favor of
  the new :term:`security policy`.

.. _upgrading_auth:

Upgrading Authentication/Authorization
--------------------------------------

The authentication and authorization policies of Pyramid 1.x have been merged
into a single :term:`security policy` in Pyramid 2.0.  Authentication and
authorization policies can still be used and will continue to function
normally, however they have been deprecated and support may be removed in
upcoming versions.

The new security policy should implement
:class:`pyramid.interfaces.ISecurityPolicy` and can be set via the
``security_policy`` argument of :class:`pyramid.config.Configurator` or
:meth:`pyramid.config.Configurator.set_security_policy`.

The policy contains ``authenticated_userid`` and ``remember``,
with the same method signatures as in the legacy authentication policy.  It
also contains ``forget``, but now with keyword arguments in the method
signature.

The new security policy adds the concept of an :term:`identity`, which is an
object representing the user associated with the current request.  The identity
can be accessed via :attr:`pyramid.request.Request.identity`.
The object can be of any shape, such as a simple ID string or an ORM object.

The concept of :term:`principals <principal>` has been removed; the
``permits`` method is passed an identity object.  This change gives much more
flexibility in authorization implementations, especially those that do not
match the ACL pattern.  If you were previously using
:class:`pyramid.authorization.ACLAuthorizationPolicy`, you can achieve the same
results by writing your own ``permits`` method using
:class:`pyramid.authorization.ACLHelper`.  For more details on implementing an
ACL, see :ref:`assigning_acls`.

Pyramid does not provide any built-in security policies.  Similiar
functionality of the authentication and authorization policies is now provided
by helpers, which can be utilized to implement your own security policy.  The
functionality of the legacy authentication policies roughly correspond to the
following helpers:

+----------------------------------------------------------------+-------------------------------------------------------------------+
| Authentication Policy                                          | Security Policy Helper                                            |
+================================================================+===================================================================+
| :class:`pyramid.authentication.SessionAuthenticationPolicy`    | :class:`pyramid.authentication.SessionAuthenticationHelper`       |
+----------------------------------------------------------------+-------------------------------------------------------------------+
| :class:`pyramid.authentication.AuthTktAuthenticationPolicy`    | :class:`pyramid.authentication.AuthTktCookieHelper`               |
+----------------------------------------------------------------+-------------------------------------------------------------------+
| :class:`pyramid.authentication.BasicAuthAuthenticationPolicy`  | Use :func:`pyramid.authentication.extract_http_basic_credentials` |
|                                                                | to retrieve credentials.                                          |
+----------------------------------------------------------------+-------------------------------------------------------------------+
| :class:`pyramid.authentication.RemoteUserAuthenticationPolicy` | ``REMOTE_USER`` can be accessed with                              |
|                                                                | ``request.environ.get('REMOTE_USER')``.                           |
+----------------------------------------------------------------+-------------------------------------------------------------------+
| :class:`pyramid.authentication.RepozeWho1AuthenticationPolicy` | No equivalent.                                                    |
+----------------------------------------------------------------+-------------------------------------------------------------------+

For further documentation on implementing security policies, see
:ref:`writing_security_policy`.

.. _behavior_of_legacy_auth:

Behavior of the Legacy System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Legacy authentication and authorization policies will continue to function as normal, as well as all related :class:`pyramid.request.Request` properties.
The new :attr:`pyramid.request.Request.identity` property will output the same result as :attr:`pyramid.request.Request.authenticated_userid`.

If using a security policy, :attr:`pyramid.request.Request.unauthenticated_userid` will return the same value as :attr:`pyramid.request.Request.authenticated_userid`.
:attr:`pyramid.request.Request.effective_principals` will always return a one-element list containing the :data:`pyramid.authorization.Everyone` principal, as there is no equivalent in the new security policy.
