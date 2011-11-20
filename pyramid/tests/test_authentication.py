import unittest
from pyramid import testing

class TestCallbackAuthenticationPolicyDebugging(unittest.TestCase):
    def setUp(self):
        from pyramid.interfaces import IDebugLogger
        self.config = testing.setUp()
        self.config.registry.registerUtility(self, IDebugLogger)
        self.messages = []

    def tearDown(self):
        del self.config
        
    def debug(self, msg):
        self.messages.append(msg)

    def _makeOne(self, userid=None, callback=None):
        from pyramid.authentication import CallbackAuthenticationPolicy
        class MyAuthenticationPolicy(CallbackAuthenticationPolicy):
            def unauthenticated_userid(self, request):
                return userid
        policy = MyAuthenticationPolicy()
        policy.debug = True
        policy.callback = callback
        return policy

    def test_authenticated_userid_no_unauthenticated_userid(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            'pyramid.tests.test_authentication.MyAuthenticationPolicy.'
            'authenticated_userid: call to unauthenticated_userid returned '
            'None; returning None')

    def test_authenticated_userid_no_callback(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne(userid='fred')
        self.assertEqual(policy.authenticated_userid(request), 'fred')
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
             "pyramid.tests.test_authentication.MyAuthenticationPolicy."
            "authenticated_userid: there was no groupfinder callback; "
            "returning 'fred'")

    def test_authenticated_userid_with_callback_fail(self):
        request = DummyRequest(registry=self.config.registry)
        def callback(userid, request):
            return None
        policy = self._makeOne(userid='fred', callback=callback)
        self.assertEqual(policy.authenticated_userid(request), None)
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            'pyramid.tests.test_authentication.MyAuthenticationPolicy.'
            'authenticated_userid: groupfinder callback returned None; '
            'returning None')

    def test_authenticated_userid_with_callback_success(self):
        request = DummyRequest(registry=self.config.registry)
        def callback(userid, request):
            return []
        policy = self._makeOne(userid='fred', callback=callback)
        self.assertEqual(policy.authenticated_userid(request), 'fred')
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            "pyramid.tests.test_authentication.MyAuthenticationPolicy."
            "authenticated_userid: groupfinder callback returned []; "
            "returning 'fred'")

    def test_effective_principals_no_unauthenticated_userid(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request),
                         ['system.Everyone'])
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            "pyramid.tests.test_authentication.MyAuthenticationPolicy."
            "effective_principals: authenticated_userid returned None; "
            "returning ['system.Everyone']")

    def test_effective_principals_no_callback(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne(userid='fred')
        self.assertEqual(
            policy.effective_principals(request),
            ['system.Everyone', 'system.Authenticated', 'fred'])
        self.assertEqual(len(self.messages), 2)
        self.assertEqual(
            self.messages[0],
            'pyramid.tests.test_authentication.MyAuthenticationPolicy.'
            'effective_principals: groupfinder callback is None, so groups '
            'is []')
        self.assertEqual(
            self.messages[1],
            "pyramid.tests.test_authentication.MyAuthenticationPolicy."
            "effective_principals: returning effective principals: "
            "['system.Everyone', 'system.Authenticated', 'fred']")

    def test_effective_principals_with_callback_fail(self):
        request = DummyRequest(registry=self.config.registry)
        def callback(userid, request):
            return None
        policy = self._makeOne(userid='fred', callback=callback)
        self.assertEqual(
            policy.effective_principals(request), ['system.Everyone'])
        self.assertEqual(len(self.messages), 2)
        self.assertEqual(
            self.messages[0],
            'pyramid.tests.test_authentication.MyAuthenticationPolicy.'
            'effective_principals: groupfinder callback returned None as '
            'groups')
        self.assertEqual(
            self.messages[1],
            "pyramid.tests.test_authentication.MyAuthenticationPolicy."
            "effective_principals: returning effective principals: "
            "['system.Everyone']")

    def test_effective_principals_with_callback_success(self):
        request = DummyRequest(registry=self.config.registry)
        def callback(userid, request):
            return []
        policy = self._makeOne(userid='fred', callback=callback)
        self.assertEqual(
            policy.effective_principals(request),
            ['system.Everyone', 'system.Authenticated', 'fred'])
        self.assertEqual(len(self.messages), 2)
        self.assertEqual(
            self.messages[0],
            'pyramid.tests.test_authentication.MyAuthenticationPolicy.'
            'effective_principals: groupfinder callback returned [] as groups')
        self.assertEqual(
            self.messages[1],
            "pyramid.tests.test_authentication.MyAuthenticationPolicy."
            "effective_principals: returning effective principals: "
            "['system.Everyone', 'system.Authenticated', 'fred']")

class TestRepozeWho1AuthenticationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.authentication import RepozeWho1AuthenticationPolicy
        return RepozeWho1AuthenticationPolicy

    def _makeOne(self, identifier_name='auth_tkt', callback=None):
        return self._getTargetClass()(identifier_name, callback)
    
    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne())

    def test_unauthenticated_userid_returns_None(self):
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid(self):
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), 'fred')

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
        from pyramid.security import Everyone
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_userid_only(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request),
                         [Everyone, Authenticated, 'fred'])

    def test_effective_principals_userid_and_groups(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred',
                                    'groups':['quux', 'biz']}})
        def callback(identity, request):
            return identity['groups']
        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.effective_principals(request),
                         [Everyone, Authenticated, 'fred', 'quux', 'biz'])

    def test_effective_principals_userid_callback_returns_None(self):
        from pyramid.security import Everyone
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
        from pyramid.authentication import RemoteUserAuthenticationPolicy
        return RemoteUserAuthenticationPolicy

    def _makeOne(self, environ_key='REMOTE_USER', callback=None):
        return self._getTargetClass()(environ_key, callback)
    
    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne())

    def test_unauthenticated_userid_returns_None(self):
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid(self):
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), 'fred')

    def test_authenticated_userid_None(self):
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)
        
    def test_authenticated_userid(self):
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), 'fred')

    def test_effective_principals_None(self):
        from pyramid.security import Everyone
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
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
        from pyramid.authentication import AuthTktAuthenticationPolicy
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
        from pyramid.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne(None, None))

    def test_unauthenticated_userid_returns_None(self):
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid(self):
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne(None, {'userid':'fred'})
        self.assertEqual(policy.unauthenticated_userid(request), 'fred')

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
        from pyramid.security import Everyone
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_callback_returns_None(self):
        from pyramid.security import Everyone
        request = DummyRequest({})
        def callback(userid, request):
            return None
        policy = self._makeOne(callback, {'userid':'fred'})
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
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
        from pyramid.authentication import AuthTktCookieHelper
        return AuthTktCookieHelper

    def _makeOne(self, *arg, **kw):
        helper = self._getTargetClass()(*arg, **kw)
        # laziness after moving auth_tkt classes and funcs into
        # authentication module
        auth_tkt = DummyAuthTktModule()
        helper.auth_tkt = auth_tkt
        helper.AuthTicket = auth_tkt.AuthTicket
        helper.parse_ticket = auth_tkt.parse_ticket
        helper.BadTicket = auth_tkt.BadTicket
        return helper

    def _makeRequest(self, cookie=None):
        environ = {'wsgi.version': (1,0)}
        environ['REMOTE_ADDR'] = '1.1.1.1'
        environ['SERVER_NAME'] = 'localhost'
        return DummyRequest(environ, cookie=cookie)

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
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.identify(request)
        self.assertEqual(result, None)

    def test_identify_cookie_value_is_None(self):
        helper = self._makeOne('secret')
        request = self._makeRequest(None)
        result = helper.identify(request)
        self.assertEqual(result, None)
        
    def test_identify_good_cookie_include_ip(self):
        helper = self._makeOne('secret', include_ip=True)
        request = self._makeRequest('ticket')
        result = helper.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], 'userid')
        self.assertEqual(result['userdata'], '')
        self.assertEqual(result['timestamp'], 0)
        self.assertEqual(helper.auth_tkt.value, 'ticket')
        self.assertEqual(helper.auth_tkt.remote_addr, '1.1.1.1')
        self.assertEqual(helper.auth_tkt.secret, 'secret')
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'],'')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_dont_include_ip(self):
        helper = self._makeOne('secret', include_ip=False)
        request = self._makeRequest('ticket')
        result = helper.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], 'userid')
        self.assertEqual(result['userdata'], '')
        self.assertEqual(result['timestamp'], 0)
        self.assertEqual(helper.auth_tkt.value, 'ticket')
        self.assertEqual(helper.auth_tkt.remote_addr, '0.0.0.0')
        self.assertEqual(helper.auth_tkt.secret, 'secret')
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'],'')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_int_useridtype(self):
        helper = self._makeOne('secret', include_ip=False)
        helper.auth_tkt.userid = '1'
        helper.auth_tkt.user_data = 'userid_type:int'
        request = self._makeRequest('ticket')
        result = helper.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], 1)
        self.assertEqual(result['userdata'], 'userid_type:int')
        self.assertEqual(result['timestamp'], 0)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'],'userid_type:int')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_nonuseridtype_user_data(self):
        helper = self._makeOne('secret', include_ip=False)
        helper.auth_tkt.userid = '1'
        helper.auth_tkt.user_data = 'bogus:int'
        request = self._makeRequest('ticket')
        result = helper.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], '1')
        self.assertEqual(result['userdata'], 'bogus:int')
        self.assertEqual(result['timestamp'], 0)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'],'bogus:int')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_unknown_useridtype(self):
        helper = self._makeOne('secret', include_ip=False)
        helper.auth_tkt.userid = 'abc'
        helper.auth_tkt.user_data = 'userid_type:unknown'
        request = self._makeRequest('ticket')
        result = helper.identify(request)
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
        helper = self._makeOne('secret', include_ip=False)
        helper.auth_tkt.userid = 'encoded'.encode('base64').strip()
        helper.auth_tkt.user_data = 'userid_type:b64str'
        request = self._makeRequest('ticket')
        result = helper.identify(request)
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
        helper = self._makeOne('secret', include_ip=False)
        helper.auth_tkt.userid = '\xc3\xa9ncoded'.encode('base64').strip()
        helper.auth_tkt.user_data = 'userid_type:b64unicode'
        request = self._makeRequest('ticket')
        result = helper.identify(request)
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
        helper = self._makeOne('secret', include_ip=True)
        helper.auth_tkt.parse_raise = True
        request = self._makeRequest('ticket')
        result = helper.identify(request)
        self.assertEqual(result, None)
    
    def test_identify_cookie_timed_out(self):
        helper = self._makeOne('secret', timeout=1)
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=bogus'})
        result = helper.identify(request)
        self.assertEqual(result, None)

    def test_identify_cookie_reissue(self):
        import time
        helper = self._makeOne('secret', timeout=10, reissue_time=0)
        now = time.time()
        helper.auth_tkt.timestamp = now
        helper.now = now + 1
        request = self._makeRequest('bogus')
        result = helper.identify(request)
        self.assertTrue(result)
        self.assertEqual(len(request.callbacks), 1)
        response = DummyResponse()
        request.callbacks[0](request, response)
        self.assertEqual(len(response.headerlist), 3)
        self.assertEqual(response.headerlist[0][0], 'Set-Cookie')

    def test_identify_cookie_reissue_already_reissued_this_request(self):
        import time
        helper = self._makeOne('secret', timeout=10, reissue_time=0)
        now = time.time()
        helper.auth_tkt.timestamp = now
        helper.now = now + 1
        request = self._makeRequest('bogus')
        request._authtkt_reissued = True
        result = helper.identify(request)
        self.assertTrue(result)
        self.assertEqual(len(request.callbacks), 0)

    def test_identify_cookie_reissue_notyet(self):
        import time
        helper = self._makeOne('secret', timeout=10, reissue_time=10)
        now = time.time()
        helper.auth_tkt.timestamp = now
        helper.now = now + 1
        request = self._makeRequest('bogus')
        result = helper.identify(request)
        self.assertTrue(result)
        self.assertEqual(len(request.callbacks), 0)

    def test_identify_cookie_reissue_revoked_by_forget(self):
        import time
        helper = self._makeOne('secret', timeout=10, reissue_time=0)
        now = time.time()
        helper.auth_tkt.timestamp = now
        helper.now = now + 1
        request = self._makeRequest('bogus')
        result = helper.identify(request)
        self.assertTrue(result)
        self.assertEqual(len(request.callbacks), 1)
        result = helper.forget(request)
        self.assertTrue(result)
        self.assertEqual(len(request.callbacks), 1)
        response = DummyResponse()
        request.callbacks[0](request, response)
        self.assertEqual(len(response.headerlist), 0)

    def test_identify_cookie_reissue_revoked_by_remember(self):
        import time
        helper = self._makeOne('secret', timeout=10, reissue_time=0)
        now = time.time()
        helper.auth_tkt.timestamp = now
        helper.auth_tkt.tokens = (u'foo',)
        helper.now = now + 1
        request = self._makeRequest('bogus')
        result = helper.identify(request)
        self.assertTrue(result)
        self.assertEqual(len(request.callbacks), 1)
        result = helper.remember(request, 'bob')
        self.assertTrue(result)
        self.assertEqual(len(request.callbacks), 1)
        response = DummyResponse()
        request.callbacks[0](request, response)
        self.assertEqual(len(response.headerlist), 0)

    def test_identify_cookie_reissue_with_tokens_default(self):
        # see https://github.com/Pylons/pyramid/issues#issue/108
        import time
        helper = self._makeOne('secret', timeout=10, reissue_time=0)
        auth_tkt = DummyAuthTktModule(tokens=[''])
        helper.auth_tkt = auth_tkt
        helper.AuthTicket = auth_tkt.AuthTicket
        helper.parse_ticket = auth_tkt.parse_ticket
        helper.BadTicket = auth_tkt.BadTicket
        now = time.time()
        helper.auth_tkt.timestamp = now
        helper.now = now + 1
        request = self._makeRequest('bogus')
        result = helper.identify(request)
        self.assertTrue(result)
        self.assertEqual(len(request.callbacks), 1)
        response = DummyResponse()
        request.callbacks[0](None, response)
        self.assertEqual(len(response.headerlist), 3)
        self.assertEqual(response.headerlist[0][0], 'Set-Cookie')
        self.assertTrue("'tokens': ()" in response.headerlist[0][1])

    def test_remember(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, 'userid')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; Path=/'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(result[1][1].endswith('; Path=/; Domain=localhost'))
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue(result[2][1].endswith('; Path=/; Domain=.localhost'))
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_include_ip(self):
        helper = self._makeOne('secret', include_ip=True)
        request = self._makeRequest()
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; Path=/'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(result[1][1].endswith('; Path=/; Domain=localhost'))
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue(result[2][1].endswith('; Path=/; Domain=.localhost'))
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_path(self):
        helper = self._makeOne('secret', include_ip=True,
                               path="/cgi-bin/app.cgi/")
        request = self._makeRequest()
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; Path=/cgi-bin/app.cgi/'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(result[1][1].endswith(
            '; Path=/cgi-bin/app.cgi/; Domain=localhost'))
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue(result[2][1].endswith(
            '; Path=/cgi-bin/app.cgi/; Domain=.localhost'))
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_http_only(self):
        helper = self._makeOne('secret', include_ip=True, http_only=True)
        request = self._makeRequest()
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; HttpOnly'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(result[1][1].endswith('; HttpOnly'))
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue(result[2][1].endswith('; HttpOnly'))
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_secure(self):
        helper = self._makeOne('secret', include_ip=True, secure=True)
        request = self._makeRequest()
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue('; Secure' in result[0][1])
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue('; Secure' in result[1][1])
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue('; Secure' in result[2][1])
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_wild_domain_disabled(self):
        helper = self._makeOne('secret', wild_domain=False)
        request = self._makeRequest()
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; Path=/'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(result[1][1].endswith('; Path=/; Domain=localhost'))
        self.assertTrue(result[1][1].startswith('auth_tkt='))

    def test_remember_domain_has_port(self):
        helper = self._makeOne('secret', wild_domain=False)
        request = self._makeRequest()
        request.environ['HTTP_HOST'] = 'example.com:80'
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; Path=/'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(result[1][1].endswith('; Path=/; Domain=example.com'))
        self.assertTrue(result[1][1].startswith('auth_tkt='))
        
    def test_remember_string_userid(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, 'userid')
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        val = self._cookieValue(values[0])
        self.assertEqual(val['userid'], 'userid'.encode('base64').strip())
        self.assertEqual(val['user_data'], 'userid_type:b64str')

    def test_remember_int_userid(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, 1)
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        val = self._cookieValue(values[0])
        self.assertEqual(val['userid'], '1')
        self.assertEqual(val['user_data'], 'userid_type:int')

    def test_remember_long_userid(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, long(1))
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        val = self._cookieValue(values[0])
        self.assertEqual(val['userid'], '1')
        self.assertEqual(val['user_data'], 'userid_type:int')

    def test_remember_unicode_userid(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        userid = unicode('\xc2\xa9', 'utf-8')
        result = helper.remember(request, userid)
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        val = self._cookieValue(values[0])
        self.assertEqual(val['userid'],
                         userid.encode('utf-8').encode('base64').strip())
        self.assertEqual(val['user_data'], 'userid_type:b64unicode')

    def test_remember_insane_userid(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        userid = object()
        result = helper.remember(request, userid)
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        value = values[0]
        self.assertTrue('userid' in value.value)

    def test_remember_max_age(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, 'userid', max_age='500')
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)

        self.assertEqual(values[0]['max-age'], '500')
        self.assertTrue(values[0]['expires'])

    def test_remember_tokens(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, 'other', tokens=('foo', 'bar'))
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue("'tokens': ('foo', 'bar')" in result[0][1])

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue("'tokens': ('foo', 'bar')" in result[1][1])

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue("'tokens': ('foo', 'bar')" in result[2][1])

    def test_remember_unicode_but_ascii_token(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        la = unicode('foo', 'utf-8')
        result = helper.remember(request, 'other', tokens=(la,))
        # tokens must be str type on both Python 2 and 3
        self.assertTrue("'tokens': ('foo',)" in result[0][1])

    def test_remember_nonascii_token(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        la = unicode('La Pe\xc3\xb1a', 'utf-8')
        self.assertRaises(ValueError, helper.remember, request, 'other',
                          tokens=(la,))

    def test_remember_invalid_token_format(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        self.assertRaises(ValueError, helper.remember, request, 'other',
                          tokens=('foo bar',))
        self.assertRaises(ValueError, helper.remember, request, 'other',
                          tokens=('1bar',))

    def test_forget(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        headers = helper.forget(request)
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

class TestAuthTicket(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.authentication import AuthTicket
        return AuthTicket(*arg, **kw)

    def test_ctor_with_tokens(self):
        ticket = self._makeOne('secret', 'userid', 'ip', tokens=('a', 'b'))
        self.assertEqual(ticket.tokens, 'a,b')

    def test_ctor_with_time(self):
        ticket = self._makeOne('secret', 'userid', 'ip', time='time')
        self.assertEqual(ticket.time, 'time')

    def test_digest(self):
        ticket = self._makeOne('secret', 'userid', '0.0.0.0', time=10)
        result = ticket.digest()
        self.assertEqual(result, '126fd6224912187ee9ffa80e0b81420c')

    def test_cookie_value(self):
        ticket = self._makeOne('secret', 'userid', '0.0.0.0', time=10,
                               tokens=('a', 'b'))
        result = ticket.cookie_value()
        self.assertEqual(result,
                         '66f9cc3e423dc57c91df696cf3d1f0d80000000auserid!a,b!')

class TestBadTicket(unittest.TestCase):
    def _makeOne(self, msg, expected=None):
        from pyramid.authentication import BadTicket
        return BadTicket(msg, expected)

    def test_it(self):
        exc = self._makeOne('msg', expected=True)
        self.assertEqual(exc.expected, True)
        self.assertTrue(isinstance(exc, Exception))

class Test_parse_ticket(unittest.TestCase):
    def _callFUT(self, secret, ticket, ip):
        from pyramid.authentication import parse_ticket
        return parse_ticket(secret, ticket, ip)

    def _assertRaisesBadTicket(self, secret, ticket, ip):
        from pyramid.authentication import BadTicket
        self.assertRaises(BadTicket,self._callFUT, secret, ticket, ip)

    def test_bad_timestamp(self):
        ticket = 'x' * 64
        self._assertRaisesBadTicket('secret', ticket, 'ip')

    def test_bad_userid_or_data(self):
        ticket = 'x' * 32 + '11111111' + 'x' * 10
        self._assertRaisesBadTicket('secret', ticket, 'ip')

    def test_digest_sig_incorrect(self):
        ticket = 'x' * 32 + '11111111' + 'a!b!c'
        self._assertRaisesBadTicket('secret', ticket, '0.0.0.0')

    def test_correct_with_user_data(self):
        ticket = '66f9cc3e423dc57c91df696cf3d1f0d80000000auserid!a,b!'
        result = self._callFUT('secret', ticket, '0.0.0.0')
        self.assertEqual(result, (10, 'userid', ['a', 'b'], ''))

class TestSessionAuthenticationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.authentication import SessionAuthenticationPolicy
        return SessionAuthenticationPolicy

    def _makeOne(self, callback=None, prefix=''):
        return self._getTargetClass()(prefix=prefix, callback=callback)

    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne())

    def test_unauthenticated_userid_returns_None(self):
        request = DummyRequest()
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid(self):
        request = DummyRequest(session={'userid':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), 'fred')

    def test_authenticated_userid_no_cookie_identity(self):
        request = DummyRequest()
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid_callback_returns_None(self):
        request = DummyRequest(session={'userid':'fred'})
        def callback(userid, request):
            return None
        policy = self._makeOne(callback)
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid(self):
        request = DummyRequest(session={'userid':'fred'})
        def callback(userid, request):
            return True
        policy = self._makeOne(callback)
        self.assertEqual(policy.authenticated_userid(request), 'fred')

    def test_effective_principals_no_identity(self):
        from pyramid.security import Everyone
        request = DummyRequest()
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_callback_returns_None(self):
        from pyramid.security import Everyone
        request = DummyRequest(session={'userid':'fred'})
        def callback(userid, request):
            return None
        policy = self._makeOne(callback)
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
        request = DummyRequest(session={'userid':'fred'})
        def callback(userid, request):
            return ['group.foo']
        policy = self._makeOne(callback)
        self.assertEqual(policy.effective_principals(request),
                         [Everyone, Authenticated, 'fred', 'group.foo'])

    def test_remember(self):
        request = DummyRequest()
        policy = self._makeOne()
        result = policy.remember(request, 'fred')
        self.assertEqual(request.session.get('userid'), 'fred')
        self.assertEqual(result, [])

    def test_forget(self):
        request = DummyRequest(session={'userid':'fred'})
        policy = self._makeOne()
        result = policy.forget(request)
        self.assertEqual(request.session.get('userid'), None)
        self.assertEqual(result, [])

    def test_forget_no_identity(self):
        request = DummyRequest()
        policy = self._makeOne()
        result = policy.forget(request)
        self.assertEqual(request.session.get('userid'), None)
        self.assertEqual(result, [])

class Test_maybe_encode(unittest.TestCase):
    def _callFUT(self, s, encoding='utf-8'):
        from pyramid.authentication import maybe_encode
        return maybe_encode(s, encoding)

    def test_unicode(self):
        result = self._callFUT(u'abc')
        self.assertEqual(result, 'abc')

class DummyContext:
    pass

class DummyCookies(object):
    def __init__(self, cookie):
        self.cookie = cookie

    def get(self, name):
        return self.cookie

class DummyRequest:
    def __init__(self, environ=None, session=None, registry=None, cookie=None):
        self.environ = environ or {}
        self.session = session or {}
        self.registry = registry
        self.callbacks = []
        self.cookies = DummyCookies(cookie)

    def add_response_callback(self, callback):
        self.callbacks.append(callback)

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

class DummyResponse:
    def __init__(self):
        self.headerlist = []
        
