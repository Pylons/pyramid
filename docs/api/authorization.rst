.. _authorization_module:

:mod:`pyramid.authorization`
-------------------------------

.. automodule:: pyramid.authorization

  .. autoclass:: ACLHelper
      :members:

  .. autoclass:: ACLAuthorizationPolicy

Constants
---------

.. attribute:: Everyone

    The special principal id named ``Everyone``.  This principal id is
    granted to all requests.  Its actual value is the string
    ``'system.Everyone'``.

    .. versionadded:: 2.0

        Moved from ``pyramid.security`` into ``pyramid.authorization``.

.. attribute:: Authenticated

    The special principal id named ``Authenticated``.  This principal id
    is granted to all requests which contain any other non-Everyone
    principal id (according to the :term:`authentication policy`).
    Its actual value is the string ``'system.Authenticated'``.

    .. versionadded:: 2.0

        Moved from ``pyramid.security`` into ``pyramid.authorization``.

.. attribute:: ALL_PERMISSIONS

    An object that can be used as the ``permission`` member of an ACE
    which matches all permissions unconditionally.  For example, an
    ACE that uses ``ALL_PERMISSIONS`` might be composed like so:
    ``('Deny', 'system.Everyone', ALL_PERMISSIONS)``.

    .. versionadded:: 2.0

        Moved from ``pyramid.security`` into ``pyramid.authorization``.

.. attribute:: DENY_ALL

    A convenience shorthand ACE that defines ``('Deny',
    'system.Everyone', ALL_PERMISSIONS)``.  This is often used as the
    last ACE in an ACL in systems that use an "inheriting" security
    policy, representing the concept "don't inherit any other ACEs".

    .. versionadded:: 2.0

        Moved from ``pyramid.security`` into ``pyramid.authorization``.

Return Values
-------------

.. autoclass:: ACLDenied
   :members: msg

   .. automethod:: __new__

    .. versionadded:: 2.0

        Moved from ``pyramid.security`` into ``pyramid.authorization``.

.. autoclass:: ACLAllowed
   :members: msg

   .. automethod:: __new__

    .. versionadded:: 2.0

        Moved from ``pyramid.security`` into ``pyramid.authorization``.
