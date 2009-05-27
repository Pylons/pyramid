from zope.interface import implements
from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.security import Everyone
from repoze.bfg.security import Authenticated

class RepozeWho1AuthenticationPolicy(object):
    """ A BFG authentication policy which obtains data from the
    repoze.who 1.X WSGI API """
    implements(IAuthenticationPolicy)
    identifier_name = 'auth_tkt'

    def _get_identity(self, request):
        return request.environ.get('repoze.who.identity')

    def _get_identifier(self, request):
        plugins = request.environ.get('repoze.who.plugins')
        if plugins is None:
            return None
        identifier = plugins[self.identifier_name]
        return identifier

    def authenticated_userid(self, context, request):
        identity = self._get_identity(request)
        if identity is None:
            return None
        return identity['repoze.who.userid']

    def effective_principals(self, context, request):
        effective_principals = [Everyone]
        identity = self._get_identity(request)
        if identity is None:
            return effective_principals

        effective_principals.append(Authenticated)
        userid = identity['repoze.who.userid']
        groups = identity.get('groups', [])
        effective_principals.append(userid)
        effective_principals.extend(groups)

        return effective_principals

    def remember(self, context, request, principal, **kw):
        identifier = self._get_identifier(request)
        if identifier is None:
            return []
        environ = request.environ
        identity = {'repoze.who.userid':principal}
        return identifier.remember(environ, identity)

    def forget(self, context, request):
        identifier = self._get_identifier(request)
        if identifier is None:
            return []
        identity = self._get_identity(request)
        return identifier.forget(request.environ, identity)
    
class RemoteUserAuthenticationPolicy(object):
    """ A BFG authentication policy which obtains data from the
    REMOTE_USER WSGI envvar """
    implements(IAuthenticationPolicy)

    def _get_identity(self, request):
        return request.environ.get('REMOTE_USER')

    def authenticated_userid(self, context, request):
        identity = self._get_identity(request)
        if identity is None:
            return None
        return identity

    def effective_principals(self, context, request):
        effective_principals = [Everyone]
        identity = self._get_identity(request)
        if identity is None:
            return effective_principals

        effective_principals.append(Authenticated)
        effective_principals.append(identity)

        return effective_principals

    def remember(self, context, request, principal, **kw):
        return []

    def forget(self, context, request):
        return []
