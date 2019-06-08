Upgrading to Pyramid 2.0
========================

Pyramid 2.0 is largely backwards compatible with the 1.x series, so minimal
changes should be necessary.  However, some 1.x functionality has been
deprecated and it is recommended to upgrade from the legacy systems.

.. _upgrading_auth:

Upgrading Authentication/Authorization
--------------------------------------

The authentication and authorization policies of Pyramid 1.x have been merged
into a single :term:`security policy` in Pyramid 2.0.  Authentication and
authorization policies can still be used and will continue to function
normally, however they have been deprecated and support may be removed in
upcoming versions.

The new security policy should implement
:interface:`pyramid.interfaces.ISecurityPolicy` and can be set via the
``security_policy`` argument of :class:`pyramid.config.Configurator` or
:meth:`pyramid.config.Configurator.set_security_policy`.

The new security policy merges ``unauthenticated_userid`` and
``authenticated_userid`` into an :term:`identity` object.  This object can be
of any shape, such as a simple ID string or an ORM object, but should   The
identity can be accessed via
:prop:`pyramid.request.Request.authenticated_identity`.

The concept of :term:`principals <principal>` has been removed; the
``permits`` method is passed an identity object.  This change gives much more
flexibility in authorization implementations, especially those that do not
match the ACL pattern.  If you were previously using
:class:`pyramid.authorization.ACLAuthorizationPolicy`, you can achieve the same
results by writing your own ``permits`` method using
:class:`pyraid.authorization.ACLHelper`.  For more details on implementing an
ACL, see :ref:`assigning_acls`.

Pyramid does not provide any built-in security policies.  Similiar
functionality of the authentication and authorization policies is now provided
by helpers, which can be utilized to easily implement your own security policy.
The functionality of the legacy authencation policies roughly correspond to the
following helpers

* :class:`pyramid.authentication.SessionAuthenticationPolicy`:
  :class:`pyramid.authentication.SessionAuthenticationHelper`
* :class:`pyramid.authentication.AuthTktAuthenticationPolicy`:
  :class:`pyramid.authentication.AuthTktCookieHelper`
* :class:`pyramid.authentication.BasicAuthAuthenticationPolicy`:
  Use :func:`pyramid.authentication.extract_http_basic_credentials` to retrieve
  credentials.
* :class:`pyramid.authentication.RemoteUserAuthenticationPolicy`:
  ``REMOTE_USER`` can be accessed with ``request.environ.get('REMOTE_USER')``.
* :class:`pyramid.authentication.RepozeWho1AuthenticationPolicy`:
  No equivalent.

For further documentation on implementing security policies, see
:ref:`writing_security_policy`.

Behavior of the Legacy System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Legacy authentication and authorization policies will continue to function as
normal, as well as all related :class:`pyramid.request.Request` properties.
The new :prop:`pyramid.request.Request.authenticated_identity` property will
output the same result as :prop:`pyramid.request.Request.authenticated_userid`.

If using a security policy,
:prop:`pyramid.request.Request.unauthenticated_userid` and
:prop:`pyramid.request.Request.authenticated_userid` will both return the
string representation of the :term:`identity`.
:prop:`pyramid.request.Request.effective_principals` will always return a
one-element list containing the :data:`pyramid.security.Everyone` principal, as
there is no equivalent in the new security policy.
