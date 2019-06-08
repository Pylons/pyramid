Upgrading to Pyramid 2.0
========================

Pyramid 2.0 was built to be backwards compatible with the 1.x series, so no
changes to your application should be necessary.  However, some functionality
has been deprecated and it is recommended to upgrade from the legacy systems.

.. _upgrade_auth:

Upgrading to a Security Policy
------------------------------

The authentication and authorization policies of Pyramid 1.x have been merged
into a single :term:`security policy` in Pyramid 2.0.  Authentication and
authorization policies will continue to function normally, however they have
been deprecated and may be removed in upcoming versions.

A security policy should implement
:interface:`pyramid.interfaces.ISecurityPolicy`.  You can set the security
policy for your application via the ``security_policy`` parameter in
:class:`pyramid.config.Configurator` or by calling
:meth:`pyramid.config.Configurator.set_security_policy`.  If you set a security
policy, you cannot set a authentication or authorization policy.

``unauthenticated_userid`` and ``authenticated_userid`` have been replaced with
the ``identify`` method.  This method should return an :term:`identity`, which
can be an object of any shape, such as a dictionary or an ORM object.  (It can
also be a simple user ID, as in the legacy authentication policy.)  The
identity can be accessed via
:meth:`pyramid.request.Request.authenticated_identity`.  If you're
using a legacy authentication policy,
:meth:`pyramid.request.Request.authenticated_identity` will return the result
of ``authenticated_userid``.

:prop:`pyramid.request.Request.unauthenticated_userid` and
:prop:`pyramid.request.Request.authenticated_userid` are deprecated but will
continue to work as normal with legacy policies.  If using a new security
policy, both properties will return the string representation of the
:term:`identity`.  :prop:`pyramid.request.Request.effective_principals` is
also deprecated and will work with legacy policies, but always return a
one-element list containing the :data:`pyramid.security.Everyone` principal
when using a security policy, as there is no equivalent in the new 
