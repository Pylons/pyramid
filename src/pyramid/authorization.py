from zope.interface import implementer

from pyramid.interfaces import IAuthorizationPolicy

from pyramid.security import ACLHelper


@implementer(IAuthorizationPolicy)
class ACLAuthorizationPolicy(object):
    """ An :term:`authorization policy` which consults an :term:`ACL`
    object attached to a :term:`context` to determine authorization
    information about a :term:`principal` or multiple principals.
    If the context is part of a :term:`lineage`, the context's parents
    are consulted for ACL information too.  The following is true
    about this security policy.

    - When checking whether the 'current' user is permitted (via the
      ``permits`` method), the security policy consults the
      ``context`` for an ACL first.  If no ACL exists on the context,
      or one does exist but the ACL does not explicitly allow or deny
      access for any of the effective principals, consult the
      context's parent ACL, and so on, until the lineage is exhausted
      or we determine that the policy permits or denies.

      During this processing, if any :data:`pyramid.security.Deny`
      ACE is found matching any principal in ``principals``, stop
      processing by returning an
      :class:`pyramid.security.ACLDenied` instance (equals
      ``False``) immediately.  If any
      :data:`pyramid.security.Allow` ACE is found matching any
      principal, stop processing by returning an
      :class:`pyramid.security.ACLAllowed` instance (equals
      ``True``) immediately.  If we exhaust the context's
      :term:`lineage`, and no ACE has explicitly permitted or denied
      access, return an instance of
      :class:`pyramid.security.ACLDenied` (equals ``False``).

    - When computing principals allowed by a permission via the
      :func:`pyramid.security.principals_allowed_by_permission`
      method, we compute the set of principals that are explicitly
      granted the ``permission`` in the provided ``context``.  We do
      this by walking 'up' the object graph *from the root* to the
      context.  During this walking process, if we find an explicit
      :data:`pyramid.security.Allow` ACE for a principal that
      matches the ``permission``, the principal is included in the
      allow list.  However, if later in the walking process that
      principal is mentioned in any :data:`pyramid.security.Deny`
      ACE for the permission, the principal is removed from the allow
      list.  If a :data:`pyramid.security.Deny` to the principal
      :data:`pyramid.security.Everyone` is encountered during the
      walking process that matches the ``permission``, the allow list
      is cleared for all principals encountered in previous ACLs.  The
      walking process ends after we've processed the any ACL directly
      attached to ``context``; a set of principals is returned.

    Objects of this class implement the
    :class:`pyramid.interfaces.IAuthorizationPolicy` interface.
    """

    def __init__(self):
        self.helper = ACLHelper()

    def permits(self, context, principals, permission):
        """ Return an instance of
        :class:`pyramid.security.ACLAllowed` instance if the policy
        permits access, return an instance of
        :class:`pyramid.security.ACLDenied` if not."""
        return self.helper.permits(context, principals, permission)

    def principals_allowed_by_permission(self, context, permission):
        """ Return the set of principals explicitly granted the
        permission named ``permission`` according to the ACL directly
        attached to the ``context`` as well as inherited ACLs based on
        the :term:`lineage`."""
        return self.helper.principals_allowed_by_permission(
            context, permission
        )
