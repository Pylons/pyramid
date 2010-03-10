from codecs import utf_8_decode
from codecs import utf_8_encode
import datetime
import time

from paste.auth import auth_tkt
from paste.request import get_cookies

from zope.interface import implements

from repoze.bfg.interfaces import IAuthenticationPolicy

from repoze.bfg.request import add_global_response_headers
from repoze.bfg.security import Authenticated
from repoze.bfg.security import Everyone

class CallbackAuthenticationPolicy(object):
    """ Abstract class """
    def authenticated_userid(self, request):
        userid = self._get_userid(request)
        if userid is None:
            return None
        if self.callback is None:
            return userid
        if self.callback(userid, request) is not None: # is not None!
            return userid

    def effective_principals(self, request):
        effective_principals = [Everyone]
        userid = self._get_userid(request)
        if userid is None:
            return effective_principals
        if self.callback is None:
            groups = []
        else:
            groups = self.callback(userid, request)
        if groups is None: # is None!
            return effective_principals
        effective_principals.append(Authenticated)
        effective_principals.append(userid)
        effective_principals.extend(groups)

        return effective_principals


class RepozeWho1AuthenticationPolicy(CallbackAuthenticationPolicy):
    """ A :mod:`repoze.bfg` :term:`authentication policy` which
    obtains data from the :mod:`repoze.who` 1.X WSGI 'API' (the
    ``repoze.who.identity`` key in the WSGI environment).

    Constructor Arguments

    ``identifier_name``

       Default: ``auth_tkt``.  The :mod:`repoze.who` plugin name that
       performs remember/forget.  Optional.

    ``callback``

        Default: ``None``.  A callback passed the :mod:`repoze.who`
        identity and the :term:`request`, expected to return ``None``
        if the user represented by the identity doesn't exist or a
        sequence of group identifiers (possibly empty) if the user
        does exist.  If ``callback`` is None, the userid will be
        assumed to exist with no groups.
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

    def authenticated_userid(self, request):
        identity = self._get_identity(request)
        if identity is None:
            return None
        if self.callback is None:
            return identity['repoze.who.userid']
        if self.callback(identity, request) is not None: # is not None!
            return identity['repoze.who.userid']

    def effective_principals(self, request):
        effective_principals = [Everyone]
        identity = self._get_identity(request)
        if identity is None:
            return effective_principals
        if self.callback is None:
            groups = []
        else:
            groups = self.callback(identity, request)
        if groups is None: # is None!
            return effective_principals
        userid = identity['repoze.who.userid']
        effective_principals.append(Authenticated)
        effective_principals.append(userid)
        effective_principals.extend(groups)

        return effective_principals

    def remember(self, request, principal, **kw):
        identifier = self._get_identifier(request)
        if identifier is None:
            return []
        environ = request.environ
        identity = {'repoze.who.userid':principal}
        return identifier.remember(environ, identity)

    def forget(self, request):
        identifier = self._get_identifier(request)
        if identifier is None:
            return []
        identity = self._get_identity(request)
        return identifier.forget(request.environ, identity)

class RemoteUserAuthenticationPolicy(CallbackAuthenticationPolicy):
    """ A :mod:`repoze.bfg` :term:`authentication policy` which
    obtains data from the ``REMOTE_USER`` WSGI environment variable.

    Constructor Arguments

    ``environ_key``

        Default: ``REMOTE_USER``.  The key in the WSGI environ which
        provides the userid.

    ``callback``

        Default: ``None``.  A callback passed the userid and the request,
        expected to return None if the userid doesn't exist or a sequence
        of group identifiers (possibly empty) if the user does exist.
        If ``callback`` is None, the userid will be assumed to exist with no
        groups.
    """
    implements(IAuthenticationPolicy)

    def __init__(self, environ_key='REMOTE_USER', callback=None):
        self.environ_key = environ_key
        self.callback = callback

    def _get_userid(self, request):
        return request.environ.get(self.environ_key)

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []

class AuthTktAuthenticationPolicy(CallbackAuthenticationPolicy):
    """ A :mod:`repoze.bfg` :term:`authentication policy` which
    obtains data from an :class:`paste.auth.auth_tkt` cookie.

    Constructor Arguments

    ``secret``

       The secret (a string) used for auth_tkt cookie encryption.
       Required.

    ``callback``

       Default: ``None``.  A callback passed the userid and the
       request, expected to return ``None`` if the userid doesn't
       exist or a sequence of group identifiers (possibly empty) if
       the user does exist.  If ``callback`` is ``None``, the userid
       will be assumed to exist with no groups.  Optional.

    ``cookie_name``

       Default: ``repoze.bfg.auth_tkt``.  The cookie name used
       (string).  Optional.

    ``secure``

       Default: ``False``.  Only send the cookie back over a secure
       conn.  Optional.

    ``include_ip``

       Default: ``False``.  Make the requesting IP address part of
       the authentication data in the cookie.  Optional.

    ``timeout``

       Default: ``None``.  Maximum number of seconds which a newly
       issued ticket will be considered valid.  After this amount of
       time, the ticket will expire (effectively logging the user
       out).  If this value is ``None``, the ticket never expires.
       Optional.

    ``reissue_time``

       Default: ``None``.  If this parameter is set, it represents the
       number of seconds that must pass before an authentication token
       cookie is reissued.  The duration is measured as the number of
       seconds since the last auth_tkt cookie was issued and 'now'.
       If the ``timeout`` value is ``None``, this parameter has no
       effect.  If this parameter is provided, and the value of
       ``timeout`` is not ``None``, the value of ``reissue_time`` must
       be smaller than value of ``timeout``.  A good rule of thumb: if
       you want auto-reissued cookies: set this to the ``timeout``
       value divided by ten.  If this value is ``0``, a new ticket
       cookie will be reissued on every request which needs
       authentication. Optional.

    ``max_age``

       Default: ``None``.  The max age of the auth_tkt cookie, in
       seconds.  This differs from ``timeout`` inasmuch as ``timeout``
       represents the lifetime of the ticket contained in the cookie,
       while this value represents the lifetime of the cookie itself.
       When this value is set, the cookie's ``Max-Age`` and
       ``Expires`` settings will be set, allowing the auth_tkt cookie
       to last between browser sessions.  It is typically nonsensical
       to set this to a value that is lower than ``timeout`` or
       ``reissue_time``, although it is not explicitly prevented.
       Optional.

    ``path``
 
       Default: ``/``. The path for which the auth_tkt cookie is valid.
       May be desirable if the application only serves part of a domain.
       Optional.
 
    ``http_only``
 
       Default: ``False``. Hide cookie from JavaScript by setting the
       HttpOnly flag. Not honored by all browsers.
       Optional.
    """
    implements(IAuthenticationPolicy)
    def __init__(self,
                 secret,
                 callback=None,
                 cookie_name='repoze.bfg.auth_tkt',
                 secure=False,
                 include_ip=False,
                 timeout=None,
                 reissue_time=None,
                 max_age=None,
                 path="/",
                 http_only=False,
                 ):
        self.cookie = AuthTktCookieHelper(
            secret,
            cookie_name=cookie_name,
            secure=secure,
            include_ip=include_ip,
            timeout=timeout,
            reissue_time=reissue_time,
            max_age=max_age,
            http_only=http_only,
            path=path,
            )
        self.callback = callback

    def _get_userid(self, request):
        result = self.cookie.identify(request)
        if result:
            return result['userid']

    def remember(self, request, principal, **kw):
        """ Accepts the following kw args: ``max_age``."""
        return self.cookie.remember(request, principal, **kw)

    def forget(self, request):
        return self.cookie.forget(request)

def b64encode(v):
    return v.encode('base64').strip().replace('\n', '')

def b64decode(v):
    return v.decode('base64')

EXPIRE = object()

class AuthTktCookieHelper(object):
    auth_tkt = auth_tkt # for tests

    userid_type_decoders = {
        'int':int,
        'unicode':lambda x: utf_8_decode(x)[0], # bw compat for old cookies
        'b64unicode': lambda x: utf_8_decode(b64decode(x))[0],
        'b64str': lambda x: b64decode(x),
        }

    userid_type_encoders = {
        int: ('int', str),
        long: ('int', str),
        unicode: ('b64unicode', lambda x: b64encode(utf_8_encode(x)[0])),
        str: ('b64str', lambda x: b64encode(x)),
        }
    
    def __init__(self, secret, cookie_name='auth_tkt', secure=False,
                 include_ip=False, timeout=None, reissue_time=None,
                 max_age=None, http_only=False, path="/"):
        self.secret = secret
        self.cookie_name = cookie_name
        self.include_ip = include_ip
        self.secure = secure
        self.timeout = timeout
        if reissue_time is not None and timeout is not None:
            if reissue_time > timeout:
                raise ValueError('reissue_time must be lower than timeout')
        self.reissue_time = reissue_time
        self.max_age = max_age
        self.http_only = http_only
        self.path = path

        static_flags = []
        if self.secure:
            static_flags.append('; Secure')
        if self.http_only:
            static_flags.append('; HttpOnly')
        self.static_flags = "".join(static_flags)

    def _get_cookies(self, environ, value, max_age=None):
        if max_age is EXPIRE:
            max_age = "; Max-Age=0; Expires=Wed, 31-Dec-97 23:59:59 GMT"
        elif max_age is not None:
            later = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=int(max_age))
            # Wdy, DD-Mon-YY HH:MM:SS GMT
            expires = later.strftime('%a, %d %b %Y %H:%M:%S GMT')
            # the Expires header is *required* at least for IE7 (IE7 does
            # not respect Max-Age)
            max_age = "; Max-Age=%s; Expires=%s" % (max_age, expires)
        else:
            max_age = ''

        cur_domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
        wild_domain = '.' + cur_domain

        cookies = [
            ('Set-Cookie', '%s="%s"; Path=%s%s%s' % (
            self.cookie_name, value, self.path, max_age, self.static_flags)),
            ('Set-Cookie', '%s="%s"; Path=%s; Domain=%s%s%s' % (
            self.cookie_name, value, self.path, cur_domain, max_age,
                self.static_flags)),
            ('Set-Cookie', '%s="%s"; Path=%s; Domain=%s%s%s' % (
            self.cookie_name, value, self.path, wild_domain, max_age,
                self.static_flags))
            ]

        return cookies

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
            timestamp, userid, tokens, user_data = self.auth_tkt.parse_ticket(
                self.secret, cookie.value, remote_addr)
        except self.auth_tkt.BadTicket:
            return None

        now = time.time()

        if self.timeout and ( (timestamp + self.timeout) < now ):
            return None

        userid_typename = 'userid_type:'
        user_data_info = user_data.split('|')
        for datum in filter(None, user_data_info):
            if datum.startswith(userid_typename):
                userid_type = datum[len(userid_typename):]
                decoder = self.userid_type_decoders.get(userid_type)
                if decoder:
                    userid = decoder(userid)

        reissue = self.reissue_time is not None
            
        if not hasattr(request, '_authtkt_reissued'):
            if reissue and ( (now - timestamp) > self.reissue_time):
                headers = self.remember(request, userid, max_age=self.max_age)
                add_global_response_headers(request, headers)
                request._authtkt_reissued = True

        environ['REMOTE_USER_TOKENS'] = tokens
        environ['REMOTE_USER_DATA'] = user_data
        environ['AUTH_TYPE'] = 'cookie'

        identity = {}
        identity['timestamp'] = timestamp
        identity['userid'] = userid
        identity['tokens'] = tokens
        identity['userdata'] = user_data
        return identity

    def forget(self, request):
        # return a set of expires Set-Cookie headers
        environ = request.environ
        return self._get_cookies(environ, '', max_age=EXPIRE)
    
    def remember(self, request, userid, max_age=None):
        max_age = max_age or self.max_age
        environ = request.environ

        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'

        user_data = ''

        encoding_data = self.userid_type_encoders.get(type(userid))
        if encoding_data:
            encoding, encoder = encoding_data
            userid = encoder(userid)
            user_data = 'userid_type:%s' % encoding
        
        ticket = self.auth_tkt.AuthTicket(
            self.secret,
            userid,
            remote_addr,
            user_data=user_data,
            cookie_name=self.cookie_name,
            secure=self.secure)

        cookie_value = ticket.cookie_value()
        return self._get_cookies(environ, cookie_value, max_age)
    
