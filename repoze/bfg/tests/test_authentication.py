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
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(context, request), None)
        
    def test_authenticated_userid(self):
        context = DummyContext()
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(context, request), 'fred')

    def test_authenticated_userid_with_callback_returns_None(self):
        context = DummyContext()
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        def callback(identity):
            return None
        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.authenticated_userid(context, request), None)

    def test_authenticated_userid_with_callback_returns_something(self):
        context = DummyContext()
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        def callback(identity):
            return ['agroup']
        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.authenticated_userid(context, request), 'fred')

    def test_effective_principals_None(self):
        from repoze.bfg.security import Everyone
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone])

    def test_effective_principals_userid_only(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        context = DummyContext()
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone, Authenticated, 'fred'])

    def test_effective_principals_userid_and_groups(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        context = DummyContext()
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred',
                                    'groups':['quux', 'biz']}})
        def callback(identity):
            return identity['groups']
        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone, Authenticated, 'fred', 'quux', 'biz'])

    def test_effective_principals_userid_callback_returns_None(self):
        from repoze.bfg.security import Everyone
        context = DummyContext()
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred',
                                    'groups':['quux', 'biz']}})
        def callback(identity):
            return None
        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone])

    def test_remember_no_plugins(self):
        context = DummyContext()
        authtkt = DummyWhoPlugin()
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.remember(context, request, 'fred')
        self.assertEqual(result, [])

    def test_remember(self):
        context = DummyContext()
        authtkt = DummyWhoPlugin()
        request = DummyRequest(
            {'repoze.who.plugins':{'auth_tkt':authtkt}})
        policy = self._makeOne()
        result = policy.remember(context, request, 'fred')
        self.assertEqual(result[0], request.environ)
        self.assertEqual(result[1], {'repoze.who.userid':'fred'})
        
    def test_forget_no_plugins(self):
        context = DummyContext()
        authtkt = DummyWhoPlugin()
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.forget(context, request)
        self.assertEqual(result, [])

    def test_forget(self):
        context = DummyContext()
        authtkt = DummyWhoPlugin()
        request = DummyRequest(
            {'repoze.who.plugins':{'auth_tkt':authtkt},
             'repoze.who.identity':{'repoze.who.userid':'fred'},
             })
        policy = self._makeOne()
        result = policy.forget(context, request)
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
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(context, request), None)
        
    def test_authenticated_userid(self):
        context = DummyContext()
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(context, request), 'fred')

    def test_effective_principals_None(self):
        from repoze.bfg.security import Everyone
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone])

    def test_effective_principals(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        context = DummyContext()
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone, Authenticated, 'fred'])

    def test_remember(self):
        context = DummyContext()
        authtkt = DummyWhoPlugin()
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        result = policy.remember(context, request, 'fred')
        self.assertEqual(result, [])
        
    def test_forget(self):
        context = DummyContext()
        authtkt = DummyWhoPlugin()
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        result = policy.forget(context, request)
        self.assertEqual(result, [])

class TestAutkTktAuthenticationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.authentication import AuthTktAuthenticationPolicy
        return AuthTktAuthenticationPolicy

    def _makeOne(self, callback, cookieidentity):
        inst = self._getTargetClass()('secret', callback)
        inst.cookie = DummyCookieHelper(cookieidentity)
        return inst

    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne(None, None))

    def test_authenticated_userid_no_cookie_identity(self):
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        self.assertEqual(policy.authenticated_userid(context, request), None)
        
    def test_authenticated_userid_callback_returns_None(self):
        context = DummyContext()
        request = DummyRequest({})
        def callback(userid):
            return None
        policy = self._makeOne(callback, {'userid':'fred'})
        self.assertEqual(policy.authenticated_userid(context, request), None)

    def test_authenticated_userid(self):
        context = DummyContext()
        request = DummyRequest({})
        def callback(userid):
            return True
        policy = self._makeOne(callback, {'userid':'fred'})
        self.assertEqual(policy.authenticated_userid(context, request), 'fred')

    def test_effective_principals_no_cookie_identity(self):
        from repoze.bfg.security import Everyone
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone])

    def test_effective_principals_callback_returns_None(self):
        from repoze.bfg.security import Everyone
        context = DummyContext()
        request = DummyRequest({})
        def callback(userid):
            return None
        policy = self._makeOne(callback, {'userid':'fred'})
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone])

    def test_effective_principals(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        context = DummyContext()
        request = DummyRequest({})
        def callback(userid):
            return ['group.foo']
        policy = self._makeOne(callback, {'userid':'fred'})
        self.assertEqual(policy.effective_principals(context, request),
                             [Everyone, Authenticated, 'fred', 'group.foo'])

    def test_remember(self):
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        result = policy.remember(context, request, 'fred')
        self.assertEqual(result, [])
        
    def test_forget(self):
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        result = policy.forget(context, request)
        self.assertEqual(result, [])

class TestAuthTktCookieHelper(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.authentication import AuthTktCookieHelper
        return AuthTktCookieHelper

    def _makeOne(self, *arg, **kw):
        plugin = self._getTargetClass()(*arg, **kw)
        return plugin

    def _makeRequest(self, kw=None):
        environ = {'wsgi.version': (1,0)}
        if kw is not None:
            environ.update(kw)
        environ['REMOTE_ADDR'] = '1.1.1.1'
        environ['SERVER_NAME'] = 'localhost'
        return DummyRequest(environ)

    def _makeTicket(self, userid='userid', remote_addr='0.0.0.0',
                    tokens = [], userdata='userdata',
                    cookie_name='auth_tkt', secure=False):
        from paste.auth import auth_tkt
        ticket = auth_tkt.AuthTicket(
            'secret',
            userid,
            remote_addr,
            tokens=tokens,
            user_data=userdata,
            cookie_name=cookie_name,
            secure=secure)
        return ticket.cookie_value()

    def test_identify_nocookie(self):
        plugin = self._makeOne('secret')
        request = self._makeRequest()
        result = plugin.identify(request)
        self.assertEqual(result, None)
        
    def test_identify_good_cookie_include_ip(self):
        plugin = self._makeOne('secret', include_ip=True)
        val = self._makeTicket(remote_addr='1.1.1.1')
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % val})
        result = plugin.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], [''])
        self.assertEqual(result['userid'], 'userid')
        self.assertEqual(result['userdata'], 'userdata')
        self.failUnless('timestamp' in result)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], [''])
        self.assertEqual(environ['REMOTE_USER_DATA'],'userdata')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_dont_include_ip(self):
        plugin = self._makeOne('secret', include_ip=False)
        val = self._makeTicket()
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % val})
        result = plugin.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], [''])
        self.assertEqual(result['userid'], 'userid')
        self.assertEqual(result['userdata'], 'userdata')
        self.failUnless('timestamp' in result)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], [''])
        self.assertEqual(environ['REMOTE_USER_DATA'],'userdata')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_int_useridtype(self):
        plugin = self._makeOne('secret', include_ip=False)
        val = self._makeTicket(userid='1', userdata='userid_type:int')
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % val})
        result = plugin.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], [''])
        self.assertEqual(result['userid'], 1)
        self.assertEqual(result['userdata'], 'userid_type:int')
        self.failUnless('timestamp' in result)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], [''])
        self.assertEqual(environ['REMOTE_USER_DATA'],'userid_type:int')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_good_cookie_unknown_useridtype(self):
        plugin = self._makeOne('secret', include_ip=False)
        val = self._makeTicket(userid='userid', userdata='userid_type:unknown')
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % val})
        result = plugin.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], [''])
        self.assertEqual(result['userid'], 'userid')
        self.assertEqual(result['userdata'], 'userid_type:unknown')
        self.failUnless('timestamp' in result)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], [''])
        self.assertEqual(environ['REMOTE_USER_DATA'],'userid_type:unknown')
        self.assertEqual(environ['AUTH_TYPE'],'cookie')

    def test_identify_bad_cookie(self):
        plugin = self._makeOne('secret', include_ip=True)
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=bogus'})
        result = plugin.identify(request)
        self.assertEqual(result, None)
    
    def test_remember_creds_same(self):
        plugin = self._makeOne('secret')
        val = self._makeTicket(userid='userid')
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % val})
        result = plugin.remember(request, 'userid', userdata='userdata')
        self.assertEqual(result, None)

    def test_remember_creds_different(self):
        plugin = self._makeOne('secret')
        old_val = self._makeTicket(userid='userid')
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % old_val})
        new_val = self._makeTicket(userid='other', userdata='userdata')
        result = plugin.remember(request, 'other', userdata='userdata')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0],
                         ('Set-Cookie',
                          'auth_tkt="%s"; Path=/' % new_val))
        self.assertEqual(result[1],
                         ('Set-Cookie',
                           'auth_tkt="%s"; Path=/; Domain=localhost'
                            % new_val))
        self.assertEqual(result[2],
                         ('Set-Cookie',
                           'auth_tkt="%s"; Path=/; Domain=.localhost'
                            % new_val))

    def test_remember_creds_different_include_ip(self):
        plugin = self._makeOne('secret', include_ip=True)
        old_val = self._makeTicket(userid='userid', remote_addr='1.1.1.1')
        request = self._makeRequest({'HTTP_COOKIE': 'auth_tkt=%s' % old_val})
        new_val = self._makeTicket(userid='other',
                                   userdata='userdata',
                                   remote_addr='1.1.1.1')
        result = plugin.remember(request, 'other', userdata='userdata')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0],
                         ('Set-Cookie',
                          'auth_tkt="%s"; Path=/' % new_val))
        self.assertEqual(result[1],
                         ('Set-Cookie',
                           'auth_tkt="%s"; Path=/; Domain=localhost'
                            % new_val))
        self.assertEqual(result[2],
                         ('Set-Cookie',
                           'auth_tkt="%s"; Path=/; Domain=.localhost'
                            % new_val))

    def test_remember_creds_different_bad_old_cookie(self):
        plugin = self._makeOne('secret')
        old_val = 'BOGUS'
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % old_val})
        new_val = self._makeTicket(userid='other', userdata='userdata')
        result = plugin.remember(request, userid='other', userdata='userdata')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0],
                         ('Set-Cookie',
                          'auth_tkt="%s"; Path=/' % new_val))
        self.assertEqual(result[1],
                         ('Set-Cookie',
                           'auth_tkt="%s"; Path=/; Domain=localhost'
                            % new_val))
        self.assertEqual(result[2],
                         ('Set-Cookie',
                           'auth_tkt="%s"; Path=/; Domain=.localhost'
                            % new_val))

    def test_remember_creds_different_with_nonstring_tokens(self):
        plugin = self._makeOne('secret')
        old_val = self._makeTicket(userid='userid')
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % old_val})
        new_val = self._makeTicket(userid='other',
                                   userdata='userdata',
                                   tokens='foo,bar',
                                  )
        result = plugin.remember(request, 'other',
                                           userdata='userdata',
                                           tokens=['foo', 'bar'],
                                          )
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0],
                         ('Set-Cookie',
                          'auth_tkt="%s"; Path=/' % new_val))
        self.assertEqual(result[1],
                         ('Set-Cookie',
                           'auth_tkt="%s"; Path=/; Domain=localhost'
                            % new_val))
        self.assertEqual(result[2],
                         ('Set-Cookie',
                           'auth_tkt="%s"; Path=/; Domain=.localhost'
                            % new_val))

    def test_remember_creds_different_int_userid(self):
        plugin = self._makeOne('secret')
        old_val = self._makeTicket(userid='userid')
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % old_val})
        new_val = self._makeTicket(userid='1', userdata='userid_type:int')
        result = plugin.remember(request, 1)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0],
                         ('Set-Cookie',
                          'auth_tkt="%s"; Path=/' % new_val))

    def test_remember_creds_different_long_userid(self):
        plugin = self._makeOne('secret')
        old_val = self._makeTicket(userid='userid')
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % old_val})
        new_val = self._makeTicket(userid='1', userdata='userid_type:int')
        result = plugin.remember(request, long(1))
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0],
                         ('Set-Cookie',
                          'auth_tkt="%s"; Path=/' % new_val))

    def test_remember_creds_different_unicode_userid(self):
        plugin = self._makeOne('secret')
        old_val = self._makeTicket(userid='userid')
        request = self._makeRequest({'HTTP_COOKIE':'auth_tkt=%s' % old_val})
        userid = unicode('\xc2\xa9', 'utf-8')
        new_val = self._makeTicket(userid=userid.encode('utf-8'),
                                   userdata='userid_type:unicode')
        result = plugin.remember(request, userid)
        self.assertEqual(type(result[0][1]), str)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0],
                         ('Set-Cookie',
                          'auth_tkt="%s"; Path=/' % new_val))

    def test_forget(self):
        plugin = self._makeOne('secret')
        request = self._makeRequest()
        headers = plugin.forget(request)
        self.assertEqual(len(headers), 3)
        header = headers[0]
        name, value = header
        self.assertEqual(name, 'Set-Cookie')
        self.assertEqual(value, 'auth_tkt=""""; Path=/')
        header = headers[1]
        name, value = header
        self.assertEqual(name, 'Set-Cookie')
        self.assertEqual(value, 'auth_tkt=""""; Path=/; Domain=localhost')
        header = headers[2]
        name, value = header
        self.assertEqual(name, 'Set-Cookie')
        self.assertEqual(value, 'auth_tkt=""""; Path=/; Domain=.localhost')


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
        return []

    def forget(self, *arg):
        return []

