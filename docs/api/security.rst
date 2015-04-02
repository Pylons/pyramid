.. _security_module:

:mod:`pyramid.security`
==========================

.. automodule:: pyramid.security

Authentication API Functions
----------------------------

.. autofunction:: authenticated_userid

.. autofunction:: unauthenticated_userid

.. autofunction:: effective_principals

.. autofunction:: forget

.. autofunction:: remember(request, userid, **kwargs)

Authorization API Functions
---------------------------

.. autofunction:: has_permission

.. autofunction:: principals_allowed_by_permission

.. autofunction:: view_execution_permitted

Constants
---------

.. attribute:: Everyone

    The special principal id named 'Everyone'.  This principal id is
    granted to all requests.  Its actual value is the string
    'system.Everyone'.

.. attribute:: Authenticated

    The special principal id named 'Authenticated'.  This principal id
    is granted to all requests which contain any other non-Everyone
    principal id (according to the :term:`authentication policy`).
    Its actual value is the string 'system.Authenticated'.

.. attribute:: ALL_PERMISSIONS

    An object that can be used as the ``permission`` member of an ACE
    which matches all permissions unconditionally.  For example, an
    ACE that uses ``ALL_PERMISSIONS`` might be composed like so:
    ``('Deny', 'system.Everyone', ALL_PERMISSIONS)``.

.. attribute:: DENY_ALL

    A convenience shorthand ACE that defines ``('Deny',
    'system.Everyone', ALL_PERMISSIONS)``.  This is often used as the
    last ACE in an ACL in systems that use an "inheriting" security
    policy, representing the concept "don't inherit any other ACEs".

.. attribute:: NO_PERMISSION_REQUIRED

	A special permission which indicates that the view should always
	be executable by entirely anonymous users, regardless of the
	default permission, bypassing any :term:`authorization policy`
	that may be in effect.  Its actual value is the string
	'__no_permission_required__'.

Return Values
-------------

.. attribute:: Allow

    The ACE "action" (the first element in an ACE e.g. ``(Allow, Everyone,
    'read')`` that means allow access.  A sequence of ACEs makes up an
    ACL.  It is a string, and its actual value is "Allow".

.. attribute:: Deny

    The ACE "action" (the first element in an ACE e.g. ``(Deny,
    'george', 'read')`` that means deny access.  A sequence of ACEs
    makes up an ACL.  It is a string, and its actual value is "Deny".

.. autoclass:: ACLDenied
   :members:

.. autoclass:: ACLAllowed
   :members:

.. autoclass:: Denied
   :members:

.. autoclass:: Allowed
   :members:

