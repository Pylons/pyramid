from zope.deprecation import deprecated
from zope.interface import implements

from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.interfaces import IAuthorizationPolicy
from repoze.bfg.interfaces import IAuthenticationPolicy

from repoze.bfg.location import lineage
from repoze.bfg.threadlocal import get_current_request

from repoze.bfg.security import Allow
from repoze.bfg.security import Deny
from repoze.bfg.security import ACLAllowed
from repoze.bfg.security import ACLDenied
from repoze.bfg.security import Everyone
from repoze.bfg.security import Authenticated

class ACLSecurityPolicy(object):
    implements(ISecurityPolicy)

    def __init__(self, get_principals):
        self.get_principals = get_principals

    def permits(self, context, request, permission):
        """ Return ``ACLAllowed`` if the policy permits access,
        ``ACLDenied`` if not. """
        principals = set(self.effective_principals(request))

        for location in lineage(context):
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            for ace in acl:
                ace_action, ace_principal, ace_permissions = ace
                if ace_principal in principals:
                    if not hasattr(ace_permissions, '__iter__'):
                        ace_permissions = [ace_permissions]
                    if permission in ace_permissions:
                        if ace_action == Allow:
                            return ACLAllowed(ace, acl, permission,
                                              principals, location)
                        else:
                            return ACLDenied(ace, acl, permission,
                                             principals, location)

            # default deny if no ACE matches in the ACL found
            result = ACLDenied(None, acl, permission, principals, location)
            return result
        
        # default deny if no ACL in lineage at all
        return ACLDenied(None, None, permission, principals, context)

    def authenticated_userid(self, request):
        principals = self.get_principals(request)
        if principals:
            return principals[0]

    def effective_principals(self, request):
        effective_principals = [Everyone]
        principal_ids = self.get_principals(request)

        if principal_ids:
            effective_principals.append(Authenticated)
            effective_principals.extend(principal_ids)

        return effective_principals

    def principals_allowed_by_permission(self, context, permission):
        for location in lineage(context):
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            allowed = {}

            for ace_action, ace_principal, ace_permissions in acl:
                if ace_action == Allow:
                    if not hasattr(ace_permissions, '__iter__'):
                        ace_permissions = [ace_permissions]
                    if permission in ace_permissions:
                        allowed[ace_principal] = True
            return sorted(allowed.keys())

        return []

class InheritingACLSecurityPolicy(object):
    """ A security policy which uses ACLs in the following ways:

    - When checking whether a user is permitted (via the ``permits``
      method), the security policy consults the ``context`` for an ACL
      first.  If no ACL exists on the context, or one does exist but
      the ACL does not explicitly allow or deny access for any of the
      effective principals, consult the context's parent ACL, and so
      on, until the lineage is exhausted or we determine that the
      policy permits or denies.

      During this processing, if any ``Deny`` ACE is found matching
      any effective principal, stop processing by returning an
      ``ACLDenied`` (equals False) immediately.  If any ``Allow`` ACE
      is found matching any effective principal, stop processing by
      returning an ``ACLAllowed`` (equals True) immediately.  If we
      exhaust the context's lneage, and no ACE has explicitly
      permitted or denied access, return an ``ACLDenied``.  This
      differs from the non-inheriting security policy (the
      ``ACLSecurityPolicy``) by virtue of the fact that it does not
      stop looking for ACLs in the object lineage after it finds the
      first one.

    - When computing principals allowed by a permission via the
      ``principals_allowed_by_permission`` method, we compute the set
      of principals that are explicitly granted the ``permission``.
      We do this by walking 'up' the object graph *from the root* to
      the context.  During this walking process, if we find an
      explicit ``Allow`` ACE for a principal that matches the
      ``permission``, the principal is included in the allow list.
      However, if later in the walking process that user is mentioned
      in any ``Deny`` ACE for the permission, the user is removed from
      the allow list.  If a ``Deny`` to the principal ``Everyone`` is
      encountered during the walking process that matches the
      ``permission``, the allow list is cleared for all principals
      encountered in previous ACLs.  The walking process ends after
      we've processed the any ACL directly attached to ``context``; a
      list of principals is returned.

    - Other aspects of this policy are the same as those in the
      ACLSecurityPolicy (e.g. ``effective_principals``,
      ``authenticated_userid``).
    """
    implements(ISecurityPolicy)

    def __init__(self, get_principals):
        self.get_principals = get_principals

    def permits(self, context, request, permission):
        """ Return ``ACLAllowed`` if the policy permits access,
        ``ACLDenied`` if not. """
        principals = set(self.effective_principals(request))
        
        for location in lineage(context):
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            for ace in acl:
                ace_action, ace_principal, ace_permissions = ace
                if ace_principal in principals:
                    if not hasattr(ace_permissions, '__iter__'):
                        ace_permissions = [ace_permissions]
                    if permission in ace_permissions:
                        if ace_action == Allow:
                            return ACLAllowed(ace, acl, permission,
                                              principals, location)
                        else:
                            return ACLDenied(ace, acl, permission,
                                             principals, location)

        # default deny if no ACL in lineage at all
        return ACLDenied(None, None, permission, principals, context)

    def authenticated_userid(self, request):
        principals = self.get_principals(request)
        if principals:
            return principals[0]

    def effective_principals(self, request):
        effective_principals = [Everyone]
        principal_ids = self.get_principals(request)

        if principal_ids:
            effective_principals.append(Authenticated)
            effective_principals.extend(principal_ids)

        return effective_principals

    def principals_allowed_by_permission(self, context, permission):
        allowed = set()

        for location in reversed(list(lineage(context))):
            # NB: we're walking *up* the object graph from the root
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            allowed_here = set()
            denied_here = set()
            
            for ace_action, ace_principal, ace_permissions in acl:
                if not hasattr(ace_permissions, '__iter__'):
                    ace_permissions = [ace_permissions]
                if ace_action == Allow and permission in ace_permissions:
                    if not ace_principal in denied_here:
                        allowed_here.add(ace_principal)
                if ace_action == Deny and permission in ace_permissions:
                    denied_here.add(ace_principal)
                    if ace_principal == Everyone:
                        # clear the entire allowed set, as we've hit a
                        # deny of Everyone ala (Deny, Everyone, ALL)
                        allowed = set()
                        break
                    elif ace_principal in allowed:
                        allowed.remove(ace_principal)

            allowed.update(allowed_here)

        return allowed

def get_remoteuser(request):
    user_id = request.environ.get('REMOTE_USER')
    if user_id:
        return [user_id]
    return []

def RemoteUserACLSecurityPolicy():
    """ A security policy which:

    - examines the request.environ for the REMOTE_USER variable and
      uses any non-false value as a principal id for this request.

    - uses an ACL-based authorization model which attempts to find the
      *first* ACL in the context' lineage.  It returns ``Allowed`` from
      its 'permits' method if the single ACL found grants access to the
      current principal.  It returns ``Denied`` if permission was not
      granted (either explicitly via a deny or implicitly by not finding
      a matching ACE action).  The *first* ACL found in the context's
      lineage is considered canonical; no searching is done for other
      security attributes after the first ACL is found in the context'
      lineage.  Use the 'inheriting' variant of this policy to consider
      more than one ACL in the lineage.

    An ACL is an ordered sequence of ACE tuples, e.g.  ``[(Allow,
    Everyone, 'read'), (Deny, 'george', 'write')]``.  ACLs stored on
    model instance objects as their ``__acl__`` attribute will be used
    by the security machinery to grant or deny access.

    Enable this security policy by adding the following to your
    application's ``configure.zcml``:

    .. code-block:: xml

       <utility
        provides="repoze.bfg.interfaces.ISecurityPolicy"
        factory="repoze.bfg.security.RemoteUserACLSecurityPolicy"
        />

    """
    return ACLSecurityPolicy(get_remoteuser)

def RemoteUserInheritingACLSecurityPolicy():
    """ A security policy which:

    - examines the request.environ for the REMOTE_USER variable and
      uses any non-false value as a principal id for this request.

    - Differs from the non-inheriting security policy variants
      (e.g. ``ACLSecurityPolicy``) by virtue of the fact that it does
      not stop looking for ACLs in the object lineage after it finds
      the first one.

    - When checking whether a user is permitted (via the ``permits``
      method), the security policy consults the ``context`` for an ACL
      first.  If no ACL exists on the context, or one does exist but
      the ACL does not explicitly allow or deny access for any of the
      effective principals, consult the context's parent ACL, and so
      on, until the lineage is exhausted or we determine that the
      policy permits or denies.

      During this processing, if any ``Deny`` ACE is found matching
      any effective principal, stop processing by returning an
      ``ACLDenied`` (equals False) immediately.  If any ``Allow`` ACE
      is found matching any effective principal, stop processing by
      returning an ``ACLAllowed`` (equals True) immediately.  If we
      exhaust the context's lneage, and no ACE has explicitly
      permitted or denied access, return an ``ACLDenied``.  

    - When computing principals allowed by a permission via the
      ``principals_allowed_by_permission`` method, we compute the set
      of principals that are explicitly granted the ``permission``.
      We do this by walking 'up' the object graph *from the root* to
      the context.  During this walking process, if we find an
      explicit ``Allow`` ACE for a principal that matches the
      ``permission``, the principal is included in the allow list.
      However, if later in the walking process that user is mentioned
      in any ``Deny`` ACE for the permission, the user is removed from
      the allow list.  If a ``Deny`` to the principal ``Everyone`` is
      encountered during the walking process that matches the
      ``permission``, the allow list is cleared for all principals
      encountered in previous ACLs.  The walking process ends after
      we've processed the any ACL directly attached to ``context``; a
      list of principals is returned.

    - Other aspects of this policy are the same as those in the
      ACLSecurityPolicy (e.g. ``effective_principals``,
      ``authenticated_userid``).

    Enable this security policy by adding the following to your
    application's ``configure.zcml``:

    .. code-block:: xml

       <utility
        provides="repoze.bfg.interfaces.ISecurityPolicy"
        factory="repoze.bfg.security.RemoteUserInheritingACLSecurityPolicy"
        />

    """
    return InheritingACLSecurityPolicy(get_remoteuser)

def get_who_principals(request):
    identity = request.environ.get('repoze.who.identity')
    if not identity:
        return []
    principals = [identity['repoze.who.userid']]
    principals.extend(identity.get('groups', []))
    return principals

def WhoACLSecurityPolicy():
    """
    A security policy which:

    - examines the request.environ for the ``repoze.who.identity``
      dictionary.  If one is found, the principal ids for the request
      are composed of ``repoze.who.identity['repoze.who.userid']``
      plus ``repoze.who.identity.get('groups', [])``.

    - uses an ACL-based authorization model which attempts to find the
      *first* ACL in the context' lineage.  It returns ``Allowed`` from
      its 'permits' method if the single ACL found grants access to the
      current principal.  It returns ``Denied`` if permission was not
      granted (either explicitly via a deny or implicitly by not finding
      a matching ACE action).  The *first* ACL found in the context's
      lineage is considered canonical; no searching is done for other
      security attributes after the first ACL is found in the context'
      lineage.  Use the 'inheriting' variant of this policy to consider
      more than one ACL in the lineage.

    An ACL is an ordered sequence of ACE tuples, e.g.  ``[(Allow,
    Everyone, 'read'), (Deny, 'george', 'write')]``.  ACLs stored on
    model instance objects as their ``__acl__`` attribute will be used
    by the security machinery to grant or deny access.

    Enable this security policy by adding the following to your
    application's ``configure.zcml``:

    .. code-block:: xml

       <utility
        provides="repoze.bfg.interfaces.ISecurityPolicy"
        factory="repoze.bfg.security.WhoACLSecurityPolicy"
        />
    """
    return ACLSecurityPolicy(get_who_principals)

RepozeWhoIdentityACLSecurityPolicy = WhoACLSecurityPolicy

deprecated('RepozeWhoIdentityACLSecurityPolicy',
           '(repoze.bfg.security.RepozeWhoIdentityACLSecurityPolicy '
           'should now be imported as '
           'repoze.bfg.security.WhoACLSecurityPolicy)',
           )

def WhoInheritingACLSecurityPolicy():
    """ A security policy which:

    - examines the request.environ for the ``repoze.who.identity``
      dictionary.  If one is found, the principal ids for the request
      are composed of ``repoze.who.identity['repoze.who.userid']``
      plus ``repoze.who.identity.get('groups', [])``.

    - Differs from the non-inheriting security policy variants
      (e.g. ``ACLSecurityPolicy``) by virtue of the fact that it does
      not stop looking for ACLs in the object lineage after it finds
      the first one.

    - When checking whether a user is permitted (via the ``permits``
      method), the security policy consults the ``context`` for an ACL
      first.  If no ACL exists on the context, or one does exist but
      the ACL does not explicitly allow or deny access for any of the
      effective principals, consult the context's parent ACL, and so
      on, until the lineage is exhausted or we determine that the
      policy permits or denies.

      During this processing, if any ``Deny`` ACE is found matching
      any effective principal, stop processing by returning an
      ``ACLDenied`` (equals False) immediately.  If any ``Allow`` ACE
      is found matching any effective principal, stop processing by
      returning an ``ACLAllowed`` (equals True) immediately.  If we
      exhaust the context's lneage, and no ACE has explicitly
      permitted or denied access, return an ``ACLDenied``.  

    - When computing principals allowed by a permission via the
      ``principals_allowed_by_permission`` method, we compute the set
      of principals that are explicitly granted the ``permission``.
      We do this by walking 'up' the object graph *from the root* to
      the context.  During this walking process, if we find an
      explicit ``Allow`` ACE for a principal that matches the
      ``permission``, the principal is included in the allow list.
      However, if later in the walking process that user is mentioned
      in any ``Deny`` ACE for the permission, the user is removed from
      the allow list.  If a ``Deny`` to the principal ``Everyone`` is
      encountered during the walking process that matches the
      ``permission``, the allow list is cleared for all principals
      encountered in previous ACLs.  The walking process ends after
      we've processed the any ACL directly attached to ``context``; a
      list of principals is returned.

    - Other aspects of this policy are the same as those in the
      ACLSecurityPolicy (e.g. ``effective_principals``,
      ``authenticated_userid``).

    Enable this security policy by adding the following to your
    application's ``configure.zcml``:

    .. code-block:: xml

       <utility
        provides="repoze.bfg.interfaces.ISecurityPolicy"
        factory="repoze.bfg.security.WhoInheritingACLSecurityPolicy"
        />
    """
    return InheritingACLSecurityPolicy(get_who_principals)


class SecurityPolicyToAuthorizationPolicyAdapter(object):
    """ An adapter registered when an old-style ISecurityPolicy
    utility is configured in ZCML instead of an IAuthorizationPolicy
    utility """
    implements(IAuthorizationPolicy)
    def __init__(self, secpol):
        self.secpol = secpol

    def permits(self, context, principals, permission):
        request = get_current_request()
        return self.secpol.permits(context, request, permission)

    def principals_allowed_by_permission(self, context, permission):
        return self.secpol.principals_allowed_by_permission(context, permission)

class SecurityPolicyToAuthenticationPolicyAdapter(object):
    implements(IAuthenticationPolicy)
    def __init__(self, secpol):
        self.secpol = secpol
        
    def authenticated_userid(self, request):
        return self.secpol.authenticated_userid(request)

    def effective_principals(self, request):
        return self.secpol.effective_principals(request)

    def remember(self, request, principal, **kw):
        return []
    
    def forget(self, request):
        return []

def registerBBBAuthn(secpol, registry):
    # Used when an explicit authentication policy is not defined, and
    # an an old-style ISecurityPolicy is registered (via ZCML), turn
    # it into separate authorization and authentication utilities
    # using adapters
    authn = SecurityPolicyToAuthenticationPolicyAdapter(secpol)
    authz = SecurityPolicyToAuthorizationPolicyAdapter(secpol)
    registry.registerUtility(authn, IAuthenticationPolicy)
    registry.registerUtility(authz, IAuthorizationPolicy)
