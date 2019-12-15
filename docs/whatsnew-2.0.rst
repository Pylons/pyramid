What's New in Pyramid 2.0
=========================

This article explains the new features in :app:`Pyramid` version 2.0 as
compared to its predecessor, :app:`Pyramid` 1.10. It also documents backwards
incompatibilities between the two versions and deprecations added to
:app:`Pyramid` 2.0, as well as software dependency changes and notable
documentation additions.

Feature Additions
-----------------

The feature additions in Pyramid 2.0 are as follows:

- The authentication and authorization policies of Pyramid 1.x have been merged
  into a single :term:`security policy` in Pyramid 2.0.  For details on how to
  migrate to the new security policy, see :ref:`upgrading_auth`.
  Authentication and authorization policies can still be used and will continue
  to function normally for the time being.

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
can be accessed via :attr:`pyramid.request.Request.authenticated_identity`.
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

Legacy authentication and authorization policies will continue to function as
normal, as well as all related :class:`pyramid.request.Request` properties.
The new :attr:`pyramid.request.Request.authenticated_identity` property will
output the same result as :attr:`pyramid.request.Request.authenticated_userid`.

If using a security policy,
:attr:`pyramid.request.Request.authenticated_userid` will return the same value
as :attr:`pyramid.request.Request.authenticated_userid`.
:attr:`pyramid.request.Request.effective_principals` will always return a
one-element list containing the :data:`pyramid.security.Everyone` principal, as
there is no equivalent in the new security policy.
