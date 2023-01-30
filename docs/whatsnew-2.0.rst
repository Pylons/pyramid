What's New in Pyramid 2.0
=========================

This article explains the new features in :app:`Pyramid` version 2.0 as compared to its predecessor, :app:`Pyramid` 1.10.
It also documents backwards incompatibilities between the two versions and deprecations added to :app:`Pyramid` 2.0, as well as software dependency changes and notable documentation additions.

.. note::

    This is the first release of :app:`Pyramid` that does not support Python 2, which is now End-of-Life and no longer receiving critical security updates by the PSF.

Bug Fix Releases
----------------

Pyramid 2.0 was released on 2021-02-28.

The following bug fix releases were made since then. Bug fix releases also include documentation improvements and other minor feature changes.

- :ref:`changes_2.0.1`

Feature Additions
-----------------

The feature additions in Pyramid 2.0 are as follows:

- The authentication and authorization policies of Pyramid 1.x have been merged into a single :term:`security policy` in Pyramid 2.0.
  For details on how to migrate to the new security policy, see :ref:`upgrading_auth_20`.
  Authentication and authorization policies can still be used and will continue to function normally for the time being.

  New security APIs have been added to support an overhaul of the authentication and authorization system.
  Read :ref:`upgrading_auth_20` for information about using this new system.

  - :meth:`pyramid.config.Configurator.set_security_policy`
  - :class:`pyramid.interfaces.ISecurityPolicy`
  - :attr:`pyramid.request.Request.identity`
  - :class:`pyramid.authentication.AuthTktCookieHelper` (available in Pyramid 1.x)
  - :class:`pyramid.authentication.SessionAuthenticationHelper`
  - :class:`pyramid.authorization.ACLHelper`

  See https://github.com/Pylons/pyramid/pull/3465

- Exposed :data:`pyramid.authorization.ALL_PERMISSIONS` and :data:`pyramid.authorization.DENY_ALL` such that all of the ACL-related constants are now importable from the ``pyramid.authorization`` namespace.
  See https://github.com/Pylons/pyramid/pull/3563

- Changed the default ``serializer`` on :class:`pyramid.session.SignedCookieSessionFactory` to use :class:`pyramid.session.JSONSerializer` instead of :class:`pyramid.session.PickleSerializer`.
  Read :ref:`upgrading_session_20` for more information about why this change was made.
  See https://github.com/Pylons/pyramid/pull/3413

- It is now possible to control whether a route pattern contains a trailing slash when it is composed with a route prefix using
  ``config.include(..., route_prefix=...)`` or ``with config.route_prefix_context(...)``.
  This can be done by specifying an empty pattern and setting the new argument ``inherit_slash=True``.
  For example:

  .. code-block:: python

      with config.route_prefix_context('/users'):
          config.add_route('users', '', inherit_slash=True)

  In the example, the resulting pattern will be ``/users``.
  Similarly, if the route prefix were ``/users/`` then the final pattern would be ``/users/``.
  If the ``pattern`` was ``'/'``, then the final pattern would always be ``/users/``.
  This new setting is only available if the pattern supplied to ``add_route`` is the empty string (``''``).
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
  However, often the case is that the data is generated when accessing some other system and then we want to cache the data for the duration of the request.
  See https://github.com/Pylons/pyramid/pull/3561

- No longer define ``pyramid.request.Request.json_body`` which is already provided by WebOb.
  This allows the attribute to now be settable.
  See https://github.com/Pylons/pyramid/pull/3447

- Improve debugging info from :class:`pyramid.view.view_config` decorator.
  See https://github.com/Pylons/pyramid/pull/3483

- ``pserve`` now outputs verbose messaging to `stderr` instead of `stdout` to circumvent buffering issues that exist by default on `stdout`.
  See https://github.com/Pylons/pyramid/pull/3593

Deprecations
------------

- Deprecated the authentication and authorization interfaces and principal-based support.
  See :ref:`upgrading_auth_20` for information on equivalent APIs and notes on upgrading.
  The following APIs are deprecated as a result of this change:

  - :meth:`pyramid.config.Configurator.set_authentication_policy`
  - :meth:`pyramid.config.Configurator.set_authorization_policy`
  - :class:`pyramid.interfaces.IAuthenticationPolicy`
  - :class:`pyramid.interfaces.IAuthorizationPolicy`
  - :attr:`pyramid.request.Request.effective_principals`
  - :attr:`pyramid.request.Request.unauthenticated_userid`
  - :class:`pyramid.authentication.AuthTktAuthenticationPolicy`
  - :class:`pyramid.authentication.RemoteUserAuthenticationPolicy`
  - :class:`pyramid.authentication.RepozeWho1AuthenticationPolicy`
  - :class:`pyramid.authentication.SessionAuthenticationPolicy`
  - :class:`pyramid.authentication.BasicAuthAuthenticationPolicy`
  - :class:`pyramid.authorization.ACLAuthorizationPolicy`
  - The ``effective_principals`` view and route predicates.

- Deprecated :func:`pyramid.security.principals_allowed_by_permission``.
  This method continues to work with the deprecated :class:`pyramid.interfaces.IAuthorizationPolicy` interface but will not work with the new :class:`pyramid.interfaces.ISecurityPolicy`.
  See https://github.com/Pylons/pyramid/pull/3465

- Deprecated several ACL-related aspects of :mod:`pyramid.security`.
  Equivalent objects should now be imported from the :mod:`pyramid.authorization` module.
  This includes:

  - :attr:`pyramid.security.Everyone`
  - :attr:`pyramid.security.Authenticated`
  - :attr:`pyramid.security.ALL_PERMISSIONS`
  - :attr:`pyramid.security.DENY_ALL`
  - :attr:`pyramid.security.ACLAllowed`
  - :attr:`pyramid.security.ACLDenied`

  See https://github.com/Pylons/pyramid/pull/3563

- Deprecated :class:`pyramid.session.PickleSerializer`.
  See :ref:`upgrading_session_20` for more information, as well as
  https://github.com/pylons/pyramid/issues/2709,
  https://github.com/pylons/pyramid/pull/3353,
  and https://github.com/pylons/pyramid/pull/3413

.. _upgrading_auth_20:

Upgrading Authentication/Authorization
--------------------------------------

.. note::
    It's important to note that the principal and ACL features within :app:`Pyramid` are not going away, nor deprecated, nor removed.
    Most ACL features are deprecated in their current locations and moved into the :mod:`pyramid.authorization` module.
    The main change is that they are now more optional than before and modifications were made to make the top-level APIs less opinionated as well as simpler.

:app:`Pyramid` provides a simple set of APIs for plugging in allowed/denied semantics in your application.

The authentication and authorization policies of Pyramid 1.x have been merged into a single :term:`security policy` in Pyramid 2.0.
Authentication and authorization policies can still be used and will continue to function normally, however they have been deprecated and support may be removed in upcoming versions.

The new security policy should implement :class:`pyramid.interfaces.ISecurityPolicy` and can be set via the ``security_policy`` argument of :class:`pyramid.config.Configurator` or :meth:`pyramid.config.Configurator.set_security_policy`.

The policy contains :meth:`pyramid.interfaces.ISecurityPolicy.authenticated_userid` and :meth:`pyramid.interfaces.ISecurityPolicy.remember`, with the same method signatures as in the legacy authentication policy.
It also contains :meth:`pyramid.interfaces.ISecurityPolicy.forget`, but now accepting keyword arguments in the method signature.

The new security policy adds the concept of an :term:`identity`, which is an object representing the user associated with the current request.
The identity can be accessed via :attr:`pyramid.request.Request.identity`.
The object can be of any shape, such as a simple ID string or an ORM object.

The concept of :term:`principals <principal>` has been removed from the request object, security policy, and view/route predicates.
Principals are replaced by ``identity``.
The :meth:`pyramid.interfaces.ISecurityPolicy.permits` method is provided the ``request``, ``context``, and ``permissions`` and may now use the ``identity`` object, or derive principals, in any way it deems necessary for the application without being restricted to a list of principals represented by strings.
This change gives much more flexibility in authorization implementations, especially those that do not match the ACL pattern.
If you were previously using :class:`pyramid.authorization.ACLAuthorizationPolicy`, you can achieve the same results by writing your own ``permits`` method using :class:`pyramid.authorization.ACLHelper`.
For more details on implementing an ACL, see :ref:`assigning_acls`.

Pyramid does not provide any built-in security policies.
Similiar functionality of the authentication and authorization policies is now provided by helpers, which can be utilized to implement your own security policy.
The functionality of the legacy authentication policies roughly correspond to the following helpers:

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

Upgrading from Built-in Policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's assume your application is using the built-in authentication and authorization policies, like :class:`pyramid.authentication.AuthTktAuthenticationPolicy`.
For example:

.. code-block:: python
    :linenos:

    def groupfinder(userid, request):
        # do some db lookups to verify userid, then return
        # None if not recognized, or a list of principals
        if userid == 'editor':
            return ['group:editor']

    authn_policy = AuthTktAuthenticationPolicy('seekrit', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

We can easily write our own :class:`pyramid.interfaces.ISecurityPolicy` implementation:

.. code-block:: python
    :linenos:

    from pyramid.authentication import AuthTktCookieHelper
    from pyramid.authorization import ACLHelper, Authenticated, Everyone

    class MySecurityPolicy:
        def __init__(self, secret):
            self.helper = AuthTktCookieHelper(secret)

        def identity(self, request):
            # define our simple identity as None or a dict with userid and principals keys
            identity = self.helper.identify(request)
            if identity is None:
                return None
            userid = identity['userid']  # identical to the deprecated request.unauthenticated_userid

            # verify the userid, just like we did before with groupfinder
            principals = groupfinder(userid, request)

            # assuming the userid is valid, return a map with userid and principals
            if principals is not None:
                return {
                    'userid': userid,
                    'principals': principals,
                }

        def authenticated_userid(self, request):
            # defer to the identity logic to determine if the user id logged in
            # and return None if they are not
            identity = request.identity
            if identity is not None:
                return identity['userid']

        def permits(self, request, context, permission):
            # use the identity to build a list of principals, and pass them
            # to the ACLHelper to determine allowed/denied
            identity = request.identity
            principals = set([Everyone])
            if identity is not None:
                principals.add(Authenticated)
                principals.add(identity['userid'])
                principals.update(identity['principals'])
            return ACLHelper().permits(context, principals, permission)

        def remember(self, request, userid, **kw):
            return self.helper.remember(request, userid, **kw)

        def forget(self, request, **kw):
            return self.helper.forget(request, **kw)

    config.set_security_policy(MySecurityPolicy('seekrit'))

This is a little bit more verbose than before, but it is easy to write, and is significantly more extensible for more advanced applications.

- Look at the new :class:`pyramid.request.RequestLocalCache` as well for help in caching the identity for improved performance.
- Look at the improved :ref:`wiki2_adding_authorization` tutorial for another example of a security policy.

For further documentation on implementing security policies, see :ref:`writing_security_policy`.

Upgrading from Third-Party Policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A generic :term:`security policy` can be written to work with legacy authentication and authorization policies.
Note that some new features like the identity may not be as extensible and nice to use when taking this approach but it can be done to ease the transition:

.. code-block:: python
    :linenos:

    class ShimSecurityPolicy:
        def __init__(self, authn_policy, authz_policy):
            self.authn_policy = authn_policy
            self.authz_policy = authz_policy

        def authenticated_userid(self, request):
            return self.authn_policy.authenticated_userid(request)

        def permits(self, request, context, permission):
            principals = self.authn_policy.effective_principals(request)
            return self.authz_policy.permits(context, principals, permission)

        def remember(self, request, userid, **kw):
            return self.authn_policy.remember(request, userid, **kw)

        def forget(self, request, **kw):
            return self.authz_policy.forget(request, **kw)

Compatibility with Legacy Authentication/Authorization Policies and APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are upgrading from an application that is using the legacy authentication and authorization policies and APIs, things will continue to function normally.
The new system is backward-compatible and the APIs still exist.
It is highly encouraged to upgrade in order to embrace the new features.
The legacy APIs are deprecated and may be removed in the future.

The new :attr:`pyramid.request.Request.identity` property will output the same result as :attr:`pyramid.request.Request.authenticated_userid`.

If you try to use the new APIs with an application that is using the legacy authentication and authorization policies, then there are some issues to be aware of:

- :attr:`pyramid.request.Request.unauthenticated_userid` will return the same value as :attr:`pyramid.request.Request.authenticated_userid`.
- :attr:`pyramid.request.Request.effective_principals` will always return a one-element list containing the :data:`pyramid.authorization.Everyone` principal.

.. index::
    triple: pickle deprecation; JSON-serializable; ISession interface

.. _upgrading_session_20:

Upgrading Session Serialization
-------------------------------

In :app:`Pyramid` 2.0 the :class:`pyramid.interfaces.ISession` interface was changed to require that session implementations only need to support JSON-serializable data types.
This is a stricter contract than the previous requirement that all objects be pickleable and it is being done for security purposes.
This is a backward-incompatible change.
Previously, if a client-side session implementation was compromised, it left the application vulnerable to remote code execution attacks using specially-crafted sessions that execute code when deserialized.

Please reference the following tickets if detailed information on these changes is needed:

- `2.0 feature request: Require that sessions are JSON serializable #2709 <https://github.com/pylons/pyramid/issues/2709>`_.
- `deprecate pickleable sessions, recommend json #3353 <https://github.com/pylons/pyramid/pull/3353>`_.
- `change to use JSONSerializer for SignedCookieSessionFactory #3413 <https://github.com/pylons/pyramid/pull/3413>`_.

For users with compatibility concerns, it's possible to craft a serializer that can handle both formats until you are satisfied that clients have had time to reasonably upgrade.
Remember that sessions should be short-lived and thus the number of clients affected should be small (no longer than an auth token, at a maximum).
An example serializer:

.. code-block:: python
    :linenos:

    import pickle
    from pyramid.session import JSONSerializer
    from pyramid.session import SignedCookieSessionFactory


    class JSONSerializerWithPickleFallback(object):
        def __init__(self):
            self.json = JSONSerializer()

        def dumps(self, appstruct):
            """
            Accept a Python object and return bytes.

            During a migration, you may want to catch serialization errors here,
            and keep using pickle while finding spots in your app that are not
            storing JSON-serializable objects. You may also want to integrate
            a fall-back to pickle serialization here as well.
            """
            return self.json.dumps(appstruct)

        def loads(self, bstruct):
            """Accept bytes and return a Python object."""
            try:
                return self.json.loads(bstruct)
            except ValueError:
                try:
                    return pickle.loads(bstruct)
                except Exception:
                    # this block should catch at least:
                    # ValueError, AttributeError, ImportError; but more to be safe
                    raise ValueError

    # somewhere in your configuration code
    serializer = JSONSerializerWithPickleFallback()
    session_factory = SignedCookieSessionFactory(..., serializer=serializer)
    config.set_session_factory(session_factory)
