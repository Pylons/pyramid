from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from pyramid.security import (
    Allow,
    Authenticated,
    Everyone,
)


USERS = {
    'editor': 'editor',
    'viewer': 'viewer',
}

GROUPS = {
    'editor': ['group:editors'],
}

class MyAuthenticationPolicy(AuthTktAuthenticationPolicy):
    def authenticated_userid(self, request):
        userid = self.unauthenticated_userid(request)
        if userid in USERS:
            return userid

    def effective_principals(self, request):
        principals = [Everyone]
        userid = self.authenticated_userid(request)
        if userid is not None:
            principals.append(Authenticated)
            principals.append(userid)

            groups = GROUPS.get(userid, [])
            principals.extend(groups)
        return principals

class RootFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:editors', 'edit'),
    ]

    def __init__(self, request):
        pass

def includeme(config):
    authn_policy = MyAuthenticationPolicy('sosecret', hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_root_factory(RootFactory)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
