import bcrypt
from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import ACLHelper
from pyramid.security import (
    Authenticated,
    Everyone,
)


def hash_password(pw):
    hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    # return unicode instead of bytes because databases handle it better
    return hashed_pw.decode('utf-8')

def check_password(expected_hash, pw):
    if expected_hash is not None:
        return bcrypt.checkpw(pw.encode('utf-8'), expected_hash.encode('utf-8'))
    return False

USERS = {
    'editor': hash_password('editor'),
    'viewer': hash_password('viewer'),
}
GROUPS = {'editor': ['group:editors']}

class MySecurityPolicy:
    def __init__(self, secret):
        self.authtkt = AuthTktCookieHelper(secret)
        self.acl = ACLHelper()

    def authenticated_identity(self, request):
        identity = self.authtkt.identify(request)
        if identity is not None and identity['userid'] in USERS:
            return identity

    def authenticated_userid(self, request):
        identity = self.authenticated_identity(request)
        if identity is not None:
            return identity['userid']

    def remember(self, request, userid, **kw):
        return self.authtkt.remember(request, userid, **kw)

    def forget(self, request, **kw):
        return self.authtkt.forget(request, **kw)

    def permits(self, request, context, permission):
        principals = self.effective_principals(request)
        return self.acl.permits(context, principals, permission)

    def effective_principals(self, request):
        principals = [Everyone]
        identity = self.authenticated_identity(request)
        if identity is not None:
            principals.append(Authenticated)
            principals.append('u:' + identity['userid'])
            principals.extend(GROUPS.get(identity['userid'], []))
        return principals

def includeme(config):
    settings = config.get_settings()

    config.set_security_policy(MySecurityPolicy(settings['auth.secret']))
