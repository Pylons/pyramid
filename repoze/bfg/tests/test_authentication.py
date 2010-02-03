import unittest

class TestRepozeWho1AuthenticationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.authentication import RepozeWho1AuthenticationPolicy
        return RepozeWho1AuthenticationPolicy

    def _makeOne(self, identifier_name='auth_tkt', callback=None):
        return self._getTargetClass()(identifier_name, callback)
    
    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne())

    def test_authenticated_userid_None(self):
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)
        
    def test_authenticated_userid(self):
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), 'fred')

    def test_authenticated_userid_with_callback_returns_None(self):
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        def callback(identity, request):
            return None
        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid_with_callback_returns_something(self):
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        def callback(identity, request):
            return ['agroup']
        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.authenticated_userid(request), 'fred')

    def test_effective_principals_None(self):
        from repoze.bfg.security import Everyone
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_userid_only(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request),
                         [Everyone, Authenticated, 'fred'])

    def test_effective_principals_userid_and_groups(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred',
                                    'groups':['quux', 'biz']}})
        def callback(identity, request):
            return identity['groups']
        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.effective_principals(request),
                         [Everyone, Authenticated, 'fred', 'quux', 'biz'])

    def test_effective_principals_userid_callback_returns_None(self):
        from repoze.bfg.security import Everyone
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred',
                                    'groups':['quux', 'biz']}})
        def callback(identity, request):
            return None
        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_remember_no_plugins(self):
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.remember(request, 'fred')
        self.assertEqual(result, [])

    def test_remember(self):
        authtkt = DummyWhoPlugin()
        request = DummyRequest(
            {'repoze.who.plugins':{'auth_tkt':authtkt}})
        policy = self._makeOne()
        result = policy.remember(request, 'fred')
        self.assertEqual(result[0], request.environ)
        self.assertEqual(result[1], {'repoze.who.userid':'fred'})
        
    def test_forget_no_plugins(self):
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.forget(request)
        self.assertEqual(result, [])

    def test_forget(self):
        authtkt = DummyWhoPlugin()
        request = DummyRequest(
            {'repoze.who.plugins':{'auth_tkt':authtkt},
             'repoze.who.identity':{'repoze.who.userid':'fred'},
             })
        policy = self._makeOne()
        result = policy.forget(request)
        self.assertEqual(result[0], request.environ)
        self.assertEqual(result[1], request.environ['repoze.who.identity'])

class TestRemoteUserAuthenticationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.authentication import RemoteUserAuthenticationPolicy
        return RemoteUserAuthenticationPolicy

    def _makeOne(self, environ_key='REMOTE_USER', callback=None):
        return self._getTargetClass()(environ_key, callback)
    
    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne())

    def test_authenticated_userid_None(self):
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)
        
    def test_authenticated_userid(self):
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), 'fred')

    def test_effective_principals_None(self):
        from repoze.bfg.security import Everyone
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request),
                         [Everyone, Authenticated, 'fred'])

    def test_remember(self):
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        result = policy.remember(request, 'fred')
        self.assertEqual(result, [])
        
    def test_forget(self):
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        result = policy.forget(request)
        self.assertEqual(result, [])

class TestAutkTktAuthenticationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.authentication import AuthTktAuthenticationPolicy
        return AuthTktAuthenticationPolicy

    def _makeOne(self, callback, cookieidentity, **kw):
        inst = self._getTargetClass()('secret', callback, **kw)
        inst.cookie = DummyCookieHelper(cookieidentity)
        return inst

    def test_allargs(self):
        # pass all known args
        inst = self._getTargetClass()(
            'secret', callback=None, cookie_name=None, secure=False,
            include_ip=False, timeout=None, reissue_time=None,
            )
        self.assertEqual(inst.callback, None)

    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne(None, None))

    def test_authenticated_userid_no_cookie_identity(self):
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        self.assertEqual(policy.authenticated_userid(request), None)
        
    def test_authenticated_userid_callback_returns_None(self):
        request = DummyRequest({})
        def callback(userid, request):
            return None
        policy = self._makeOne(callback, {'userid':'fred'})
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid(self):
        request = DummyRequest({})
        def callback(userid, request):
            return True
        policy = self._makeOne(callback, {'userid':'fred'})
        self.assertEqual(policy.authenticated_userid(request), 'fred')

    def test_effective_principals_no_cookie_identity(self):
        from repoze.bfg.security import Everyone
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_callback_returns_None(self):
        from repoze.bfg.security import Everyone
        request = DummyRequest({})
        def callback(userid, request):
            return None
        policy = self._makeOne(callback, {'userid':'fred'})
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        request = DummyRequest({})
        def callback(userid, request):
            return ['group.foo']
        policy = self._makeOne(callback, {'userid':'fred'})
        self.assertEqual(policy.effective_principals(request),
                             [Everyone, Authenticated, 'fred', 'group.foo'])

    def test_remember(self):
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        result = policy.remember(request, 'fred')
        self.assertEqual(result, [])

    def test_remember_with_extra_kargs(self):
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        result = policy.remember(request, 'fred', a=1, b=2)
        self.assertEqual(policy.cookie.kw, {'a':1, 'b':2})
        self.assertEqual(result, [])
        
    def test_forget(self):
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        result = policy.forget(request)
        self.assertEqual(result, [])

class TestAuthTktCookieHelper(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.authentication import AuthTktCookieHelper
        return AuthTktCookieHelper

    def _makeOne(self, *arg, **kw):
        plugin = self._getTargetClass()(*arg, **kw)
        plugin.auth_tkt = DummyAuthTktModule()
        return plugin

    def _makeRequest(self, kw=None):
        environ = {'wsgi.version': (1,0)}
        if kw is not None:
            environ.update(kw)
        environ['REMOTE_ADDR'] = '1.1.1.1'
        environ['SERVER_NAME'] = 'localhost'
        return DummyRequest(environ)

    def _cookieValue(self, cookie):
        return eval(cookie.value)

    def _parseHeaders(self, headers):
        return [ self._parseHeader(header) for header in headers ]

    def _parseHeader(self, header):
        cookie = self._parseCookie(header[1])
        return cookie

    def _parseCookie(self, cookie):
        from Cookie import SimpleCookie
        cookies = SimpleCookie()
        cookies.load(cookie)
        return cookies.get('auth_tkt')

    def test_identify_nocookie(self):
        plugin = self._makeOne('secret')
        request = self._makeRequest()
        result = plugin.identify(request)
        self.assertEqual(result, None)
        
    def test_identify_good_cookie_include_ip(self):
        plugin = self._makeOne('secret', include_ip=True)
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=ticket'})
        result = plugin.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], 'userid')
        self.assertEqual(result['userdata'], '')
        self.assertEqual(result['timestamp'], 0)
        self.assertEqual(plugin.auth_tkt.value, 'ticket')
        self.assertEqual(plugin.auth_tkt.remote_addr, '1.1.1.1')
        self.assertEqual(plugin.auth_tkt.secret, 'secret')
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'],'')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_dont_include_ip(self):
        plugin = self._makeOne('secret', include_ip=False)
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=ticket'})
        result = plugin.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], 'userid')
        self.assertEqual(result['userdata'], '')
        self.assertEqual(result['timestamp'], 0)
        self.assertEqual(plugin.auth_tkt.value, 'ticket')
        self.assertEqual(plugin.auth_tkt.remote_addr, '0.0.0.0')
        self.assertEqual(plugin.auth_tkt.secret, 'secret')
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'],'')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_int_useridtype(self):
        plugin = self._makeOne('secret', include_ip=False)
        plugin.auth_tkt.userid = '1'
        plugin.auth_tkt.user_data = 'userid_type:int'
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=ticket'})
        result = plugin.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], 1)
        self.assertEqual(result['userdata'], 'userid_type:int')
        self.assertEqual(result['timestamp'], 0)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'],'userid_type:int')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_unknown_useridtype(self):
        plugin = self._makeOne('secret', include_ip=False)
        plugin.auth_tkt.userid = 'abc'
        plugin.auth_tkt.user_data = 'userid_type:unknown'
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=ticket'})
        result = plugin.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], 'abc')
        self.assertEqual(result['userdata'], 'userid_type:unknown')
        self.assertEqual(result['timestamp'], 0)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'],'userid_type:unknown')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_b64str_useridtype(self):
        plugin = self._makeOne('secret', include_ip=False)
        plugin.auth_tkt.userid = 'encoded'.encode('base64').strip()
        plugin.auth_tkt.user_data = 'userid_type:b64str'
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=ticket'})
        result = plugin.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], 'encoded')
        self.assertEqual(result['userdata'], 'userid_type:b64str')
        self.assertEqual(result['timestamp'], 0)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'],'userid_type:b64str')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_b64unicode_useridtype(self):
        plugin = self._makeOne('secret', include_ip=False)
        plugin.auth_tkt.userid = '\xc3\xa9ncoded'.encode('base64').strip()
        plugin.auth_tkt.user_data = 'userid_type:b64unicode'
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=ticket'})
        result = plugin.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], unicode('\xc3\xa9ncoded', 'utf-8'))
        self.assertEqual(result['userdata'], 'userid_type:b64unicode')
        self.assertEqual(result['timestamp'], 0)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'],'userid_type:b64unicode')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_bad_cookie(self):
        plugin = self._makeOne('secret', include_ip=True)
        plugin.auth_tkt.parse_raise = True
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=bogus'})
        result = plugin.identify(request)
        self.assertEqual(result, None)
    
    def test_identify_cookie_timed_out(self):
        plugin = self._makeOne('secret', timeout=1)
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=bogus'})
        result = plugin.identify(request)
        self.assertEqual(result, None)

    def test_identify_cookie_reissue(self):
        import time
        plugin = self._makeOne('secret', timeout=5, reissue_time=0)
        plugin.auth_tkt.timestamp = time.time()
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=bogus'})
        result = plugin.identify(request)
        self.failUnless(result)
        response_headers = request.global_response_headers
        self.assertEqual(len(response_headers), 3)
        self.assertEqual(response_headers[0][0], 'Set-Cookie')

    def test_remember(self):
        plugin = self._makeOne('secret')
        request = self._makeRequest()
        result = plugin.remember(request, 'userid')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.failUnless(result[0][1].endswith('; Path=/'))
        self.failUnless(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.failUnless(result[1][1].endswith('; Path=/; Domain=localhost'))
        self.failUnless(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.failUnless(result[2][1].endswith('; Path=/; Domain=.localhost'))
        self.failUnless(result[2][1].startswith('auth_tkt='))

    def test_remember_include_ip(self):
        plugin = self._makeOne('secret', include_ip=True)
        request = self._makeRequest()
        result = plugin.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.failUnless(result[0][1].endswith('; Path=/'))
        self.failUnless(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.failUnless(result[1][1].endswith('; Path=/; Domain=localhost'))
        self.failUnless(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.failUnless(result[2][1].endswith('; Path=/; Domain=.localhost'))
        self.failUnless(result[2][1].startswith('auth_tkt='))

    def test_remember_path(self):
        plugin = self._makeOne('secret', include_ip=True,
                               path="/cgi-bin/bfg.cgi/")
        request = self._makeRequest()
        result = plugin.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.failUnless(result[0][1].endswith('; Path=/cgi-bin/bfg.cgi/'))
        self.failUnless(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.failUnless(result[1][1].endswith(
            '; Path=/cgi-bin/bfg.cgi/; Domain=localhost'))
        self.failUnless(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.failUnless(result[2][1].endswith(
            '; Path=/cgi-bin/bfg.cgi/; Domain=.localhost'))
        self.failUnless(result[2][1].startswith('auth_tkt='))

    def test_remember_http_only(self):
        plugin = self._makeOne('secret', include_ip=True, http_only=True)
        request = self._makeRequest()
        result = plugin.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.failUnless(result[0][1].endswith('; HttpOnly'))
        self.failUnless(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.failUnless(result[1][1].endswith('; HttpOnly'))
        self.failUnless(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.failUnless(result[2][1].endswith('; HttpOnly'))
        self.failUnless(result[2][1].startswith('auth_tkt='))

    def test_remember_secure(self):
        plugin = self._makeOne('secret', include_ip=True, secure=True)
        request = self._makeRequest()
        result = plugin.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.failUnless('; Secure' in result[0][1])
        self.failUnless(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.failUnless('; Secure' in result[1][1])
        self.failUnless(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.failUnless('; Secure' in result[2][1])
        self.failUnless(result[2][1].startswith('auth_tkt='))

    def test_remember_string_userid(self):
        plugin = self._makeOne('secret')
        request = self._makeRequest()
        result = plugin.remember(request, 'userid')
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        val = self._cookieValue(values[0])
        self.assertEqual(val['userid'], 'userid'.encode('base64').strip())
        self.assertEqual(val['user_data'], 'userid_type:b64str')

    def test_remember_int_userid(self):
        plugin = self._makeOne('secret')
        request = self._makeRequest()
        result = plugin.remember(request, 1)
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        val = self._cookieValue(values[0])
        self.assertEqual(val['userid'], '1')
        self.assertEqual(val['user_data'], 'userid_type:int')

    def test_remember_long_userid(self):
        plugin = self._makeOne('secret')
        request = self._makeRequest()
        result = plugin.remember(request, long(1))
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        val = self._cookieValue(values[0])
        self.assertEqual(val['userid'], '1')
        self.assertEqual(val['user_data'], 'userid_type:int')

    def test_remember_unicode_userid(self):
        plugin = self._makeOne('secret')
        request = self._makeRequest()
        userid = unicode('\xc2\xa9', 'utf-8')
        result = plugin.remember(request, userid)
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        val = self._cookieValue(values[0])
        self.assertEqual(val['userid'],
                         userid.encode('utf-8').encode('base64').strip())
        self.assertEqual(val['user_data'], 'userid_type:b64unicode')

    def test_remember_max_age(self):
        plugin = self._makeOne('secret')
        request = self._makeRequest()
        result = plugin.remember(request, 'userid', max_age='500')
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)

        self.assertEqual(values[0]['max-age'], '500')
        self.failUnless(values[0]['expires'])
        
    def test_forget(self):
        plugin = self._makeOne('secret')
        request = self._makeRequest()
        headers = plugin.forget(request)
        self.assertEqual(len(headers), 3)
        name, value = headers[0]
        self.assertEqual(name, 'Set-Cookie')
        self.assertEqual(value,
          'auth_tkt=""; Path=/; Max-Age=0; Expires=Wed, 31-Dec-97 23:59:59 GMT')
        name, value = headers[1]
        self.assertEqual(name, 'Set-Cookie')
        self.assertEqual(value,
                         'auth_tkt=""; Path=/; Domain=localhost; Max-Age=0; '
                         'Expires=Wed, 31-Dec-97 23:59:59 GMT')
        name, value = headers[2]
        self.assertEqual(name, 'Set-Cookie')
        self.assertEqual(value,
                         'auth_tkt=""; Path=/; Domain=.localhost; Max-Age=0; '
                         'Expires=Wed, 31-Dec-97 23:59:59 GMT')

    def test_timeout_lower_than_reissue(self):
        self.assertRaises(ValueError, self._makeOne, 'userid', timeout=1,
                          reissue_time=2)

class DummyContext:
    pass

class DummyRequest:
    def __init__(self, environ):
        self.environ = environ

class DummyWhoPlugin:
    def remember(self, environ, identity):
        return environ, identity
    
    def forget(self, environ, identity):
        return environ, identity

class DummyCookieHelper:
    def __init__(self, result):
        self.result = result

    def identify(self, *arg, **kw):
        return self.result

    def remember(self, *arg, **kw):
        self.kw = kw
        return []

    def forget(self, *arg):
        return []

class DummyAuthTktModule(object):
    def __init__(self, timestamp=0, userid='userid', tokens=(), user_data='',
                 parse_raise=False):
        self.timestamp = timestamp
        self.userid = userid
        self.tokens = tokens
        self.user_data = user_data
        self.parse_raise = parse_raise
        def parse_ticket(secret, value, remote_addr):
            self.secret = secret
            self.value = value
            self.remote_addr = remote_addr
            if self.parse_raise:
                raise self.BadTicket()
            return self.timestamp, self.userid, self.tokens, self.user_data
        self.parse_ticket = parse_ticket
        
        class AuthTicket(object):
            def __init__(self, secret, userid, remote_addr, **kw):
                self.secret = secret
                self.userid = userid
                self.remote_addr = remote_addr
                self.kw = kw

            def cookie_value(self):
                result = {'secret':self.secret, 'userid':self.userid,
                          'remote_addr':self.remote_addr}
                result.update(self.kw)
                result = repr(result)
                return result
        self.AuthTicket = AuthTicket

    class BadTicket(Exception):
        pass

