.. _security_module:

:mod:`repoze.bfg.security`
==========================

.. automodule:: repoze.bfg.security

  .. autofunction:: authenticated_userid

  .. autofunction:: effective_principals

  .. autofunction:: has_permission

  .. autofunction:: principals_allowed_by_permission

  .. attribute:: Everyone

    The special principal id named 'Everyone'.  This principal id is
    granted to all requests.  Its actual value is the string
    'system.Everyone'.

  .. attribute:: Authenticated

    The special principal id named 'Authenticated'.  This principal id
    is granted to all requests which contain any other non-Everyone
    principal id (according to the security policy).  Its actual value
    is the string 'system.Authenticated'.

  .. attribute:: Allow

    The ACE "action" (the first element in an ACE e.g. ``(Allow, Everyone,
    'read')`` that means allow access.  A sequence of ACEs makes up an
    ACL.  It is a string, and it's actual value is "Allow".

  .. attribute:: Deny

    The ACE "action" (the first element in an ACE e.g. ``(Deny,
    'george', 'read')`` that means deny access.  A sequence of ACEs
    makes up an ACL.  It is a string, and it's actual value is "Deny".

  .. autoclass:: Denied
     :members:

  .. autoclass:: Allowed
     :members:

