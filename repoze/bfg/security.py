from zope.interface import implements
from zope.location.location import LocationIterator

from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import IViewPermissionFactory
from repoze.bfg.interfaces import NoAuthorizationInformation

Everyone = 'system.Everyone'
Authenticated = 'system.Authenticated'
Allow = 'Allow'
Deny = 'Deny'

class ACLAuthorizer(object):

    def __init__(self, context, logger=None):
        self.context = context
        self.logger = logger

    def get_acl(self, default=None):
        return getattr(self.context, '__acl__', default)

    def permits(self, permission, *principals):
        acl = self.get_acl()
        if acl is None:
            raise NoAuthorizationInformation('%s item has no __acl__' % acl)

        for ace in acl:
            ace_action, ace_principal, ace_permissions = ace
            for principal in flatten(principals):
                if ace_principal == principal:
                    permissions = flatten(ace_permissions)
                    if permission in permissions:
                        action = ace_action
                        if action == Allow:
                            result = Allowed(ace, acl, permission, principals,
                                             self.context)
                            self.logger and self.logger.debug(str(result))
                            return result
                        result = Denied(ace, acl, permission, principals,
                                        self.context)
                        self.logger and self.logger.debug(str(result))
                        return result
        result = Denied(None, acl, permission, principals, self.context)
        self.logger and self.logger.debug(str(result))
        return result
        

class RemoteUserACLSecurityPolicy(object):
    implements(ISecurityPolicy)
    authorizer_factory = ACLAuthorizer
    
    def __init__(self, logger=None):
        self.logger = logger

    def permits(self, context, request, permission):
        userid = request.environ.get('REMOTE_USER', None)
        effective_principals = [Everyone]

        if userid is not None:
            effective_principals.append(Authenticated)
            effective_principals.append(userid)

        for location in LocationIterator(context):
            authorizer = self.authorizer_factory(context, self.logger)
            try:
                return authorizer.permits(permission, *effective_principals)
            except NoAuthorizationInformation:
                continue

        return False

class PermitsResult:
    def __init__(self, ace, acl, permission, principals, context):
        self.acl = acl
        self.ace = ace
        self.permission = permission
        self.principals = principals
        self.context_repr = repr(context)

    def __str__(self):
        msg = '%s: %r via ace %r in acl %s or principals %r in context %s'
        msg = msg % (self.__class__.__name__,
                     self.permission, self.ace, self.acl, self.principals,
                     self.context_repr)
        return msg

class Denied(PermitsResult):
    def __nonzero__(self):
        return False

    def __eq__(self, other):
        if bool(other) is False:
            return True

class Allowed(PermitsResult):
    def __nonzero__(self):
        return True

    def __eq__(self, other):
        if bool(other) is True:
            return True

def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""
    if isinstance(x, basestring):
        return [x]
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

class ViewPermission(object):
    implements(IViewPermission)
    def __init__(self, context, request, permission_name):
        self.context = context
        self.request = request
        self.permission_name = permission_name
    
    def __call__(self, security_policy):
        return security_policy.permits(self.context, self.request,
                                       self.permission_name)

    def __repr__(self):
        return '<Permission at %s named %r for %r>' % (id(self),
                                                       self.permission_name,
                                                       self.request.view_name)
        
class ViewPermissionFactory(object):
    implements(IViewPermissionFactory)
    def __init__(self, permission_name):
        self.permission_name = permission_name

    def __call__(self, context, request):
        return ViewPermission(context, request, self.permission_name)

    
