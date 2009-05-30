from codecs import utf_8_decode
from codecs import utf_8_encode
import crypt
import os
import stat
import StringIO
import time
import traceback

from paste.request import get_cookies
from paste.auth import auth_tkt

from zope.interface import implements
from zope.component import queryUtility

from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.security import Everyone
from repoze.bfg.security import Authenticated

class CallbackAuthenticationPolicy(object):
    """ Abstract class """
    def authenticated_userid(self, context, request):
        userid = self._get_userid(request)
        if userid is None:
            return None
        if self.callback is None:
            return userid
        if self.callback(userid) is not None: # is not None!
            return userid

    def effective_principals(self, context, request):
        effective_principals = [Everyone]
        userid = self._get_userid(request)
        if userid is None:
            return effective_principals
        if self.callback is None:
            groups = []
        else:
            groups = self.callback(userid)
        if groups is None: # is None!
            return effective_principals
        effective_principals.append(Authenticated)
        effective_principals.append(userid)
        effective_principals.extend(groups)

        return effective_principals


class RepozeWho1AuthenticationPolicy(CallbackAuthenticationPolicy):
    """ A BFG authentication policy which obtains data from the
    repoze.who 1.X WSGI 'API' (the ``repoze.who.identity`` key in the
    WSGI environment).

    Constructor Arguments

    ``identifier_name``

       Default: ``auth_tkt``.  The who plugin name that performs
       remember/forget.  Optional.

    ``callback``

        Default: ``None``.  A callback passed the repoze.who identity,
        expected to return None if the user represented by the
        identity doesn't exist or a sequence of group identifiers
        (possibly empty) if the user does exist.  If ``callback`` is
        None, the userid will be assumed to exist with no groups.

    """
    implements(IAuthenticationPolicy)

    def __init__(self, identifier_name='auth_tkt', callback=None):
        self.identifier_name = identifier_name
        self.callback = callback

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
        if self.callback is None:
            return identity['repoze.who.userid']
        if self.callback(identity) is not None: # is not None!
            return identity['repoze.who.userid']

    def effective_principals(self, context, request):
        effective_principals = [Everyone]
        identity = self._get_identity(request)
        if identity is None:
            return effective_principals
        if self.callback is None:
            groups = []
        else:
            groups = self.callback(identity)
        if groups is None: # is None!
            return effective_principals
        userid = identity['repoze.who.userid']
        effective_principals.append(Authenticated)
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

class RemoteUserAuthenticationPolicy(CallbackAuthenticationPolicy):
    """ A BFG authentication policy which obtains data from the
    REMOTE_USER WSGI envvar.

    Constructor Arguments

    ``environ_key``

        Default: ``REMOTE_USER``.  The key in the WSGI environ which
        provides the userid.

    ``callback``

        Default: ``None``.  A callback passed the userid, expected to return
        None if the userid doesn't exist or a sequence of group identifiers
        (possibly empty) if the user does exist.  If ``callback`` is None,
        the userid will be assumed to exist with no groups.
    """
    implements(IAuthenticationPolicy)

    def __init__(self, environ_key='REMOTE_USER', callback=None):
        self.environ_key = environ_key
        self.callback = callback

    def _get_userid(self, request):
        return request.environ.get(self.environ_key)

    def remember(self, context, request, principal, **kw):
        return []

    def forget(self, context, request):
        return []

class AuthTktAuthenticationPolicy(CallbackAuthenticationPolicy):
    """ A BFG authentication policy which obtains data from an
    auth_tkt cookie.

    Constructor Arguments

    ``secret``

       The secret (a string) used for auth_tkt cookie encryption.
       Required.

    ``callback``

       Default: ``None``.  A callback passed the userid, expected to return
       None if the userid doesn't exist or a sequence of group identifiers
       (possibly empty) if the user does exist.  If ``callback`` is None,
       the userid will be assumed to exist with no groups.

    ``cookie_name``

       Default: ``repoze.bfg.auth_tkt``.  The cookie name used
       (string).  Optional.

    ``secure``

       Default: ``False``.  Only send the cookie back over a secure
       conn.  Optional.

    ``include_ip``

       Default: ``False``.  Make the requesting IP address part of
       the authentication data in the cookie.  Optional.

    """
    implements(IAuthenticationPolicy)
    def __init__(self,
                 secret,
                 callback=None,
                 cookie_name='repoze.bfg.auth_tkt',
                 secure=False,
                 include_ip=False):
        self.cookie = AuthTktCookieHelper(
            secret,
            cookie_name=cookie_name,
            secure=secure,
            include_ip=include_ip,
            )
        self.callback = callback

    def _get_userid(self, request):
        result = self.cookie.identify(request)
        if result:
            return result['userid']

    def remember(self, context, request, principal, **kw):
        return self.cookie.remember(request, principal)

    def forget(self, context, request):
        return self.cookie.forget(request)
        
class AuthTktCookieHelper(object):
    userid_type_decoders = {
        'int':int,
        'unicode':lambda x: utf_8_decode(x)[0],
        }

    userid_type_encoders = {
        int: ('int', str),
        long: ('int', str),
        unicode: ('unicode', lambda x: utf_8_encode(x)[0]),
        }
    
    def __init__(self, secret, cookie_name='auth_tkt', secure=False,
                 include_ip=False):
        self.secret = secret
        self.cookie_name = cookie_name
        self.include_ip = include_ip
        self.secure = secure

    # IIdentifier
    def identify(self, request):
        environ = request.environ
        cookies = get_cookies(environ)
        cookie = cookies.get(self.cookie_name)

        if cookie is None or not cookie.value:
            return None

        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'
        
        try:
            timestamp, userid, tokens, user_data = auth_tkt.parse_ticket(
                self.secret, cookie.value, remote_addr)
        except auth_tkt.BadTicket:
            return None

        userid_typename = 'userid_type:'
        user_data_info = user_data.split('|')
        for datum in filter(None, user_data_info):
            if datum.startswith(userid_typename):
                userid_type = datum[len(userid_typename):]
                decoder = self.userid_type_decoders.get(userid_type)
                if decoder:
                    userid = decoder(userid)
            
        environ['REMOTE_USER_TOKENS'] = tokens
        environ['REMOTE_USER_DATA'] = user_data
        environ['AUTH_TYPE'] = 'cookie'

        identity = {}
        identity['timestamp'] = timestamp
        identity['userid'] = userid
        identity['tokens'] = tokens
        identity['userdata'] = user_data
        return identity

    def _get_cookies(self, environ, value):
        cur_domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
        wild_domain = '.' + cur_domain
        cookies = [
            ('Set-Cookie', '%s="%s"; Path=/' % (
            self.cookie_name, value)),
            ('Set-Cookie', '%s="%s"; Path=/; Domain=%s' % (
            self.cookie_name, value, cur_domain)),
            ('Set-Cookie', '%s="%s"; Path=/; Domain=%s' % (
            self.cookie_name, value, wild_domain))
            ]
        return cookies

    # IIdentifier
    def forget(self, request):
        # return a set of expires Set-Cookie headers
        environ = request.environ
        return self._get_cookies(environ, '""')
    
    # IIdentifier
    def remember(self, request, userid, tokens='', userdata=''):
        environ = request.environ
        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'

        cookies = get_cookies(environ)
        old_cookie = cookies.get(self.cookie_name)
        existing = cookies.get(self.cookie_name)
        old_cookie_value = getattr(existing, 'value', None)

        timestamp, old_userid, old_tokens, old_userdata = None, '', '', ''

        if old_cookie_value:
            try:
                (timestamp,old_userid,old_tokens,
                 old_userdata) = auth_tkt.parse_ticket(
                    self.secret, old_cookie_value, remote_addr)
            except auth_tkt.BadTicket:
                pass

        encoding_data = self.userid_type_encoders.get(type(userid))
        if encoding_data:
            encoding, encoder = encoding_data
            userid = encoder(userid)
            userdata = 'userid_type:%s' % encoding
        
        if not isinstance(tokens, basestring):
            tokens = ','.join(tokens)
        if not isinstance(old_tokens, basestring):
            old_tokens = ','.join(old_tokens)
        old_data = (old_userid, old_tokens, old_userdata)
        new_data = (userid, tokens, userdata)

        if old_data != new_data:
            ticket = auth_tkt.AuthTicket(
                self.secret,
                userid,
                remote_addr,
                tokens=tokens,
                user_data=userdata,
                cookie_name=self.cookie_name,
                secure=self.secure)
            new_cookie_value = ticket.cookie_value()
            
            cur_domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
            wild_domain = '.' + cur_domain
            if old_cookie_value != new_cookie_value:
                # return a set of Set-Cookie headers
                return self._get_cookies(environ, new_cookie_value)
    
