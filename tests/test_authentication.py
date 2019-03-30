import unittest
import warnings
from pyramid import testing
from pyramid.util import bytes_


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
            'tests.test_authentication.MyAuthenticationPolicy.'
            'authenticated_userid: call to unauthenticated_userid returned '
            'None; returning None',
        )

    def test_authenticated_userid_no_callback(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne(userid='fred')
        self.assertEqual(policy.authenticated_userid(request), 'fred')
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            "tests.test_authentication.MyAuthenticationPolicy."
            "authenticated_userid: there was no groupfinder callback; "
            "returning 'fred'",
        )

    def test_authenticated_userid_with_callback_fail(self):
        request = DummyRequest(registry=self.config.registry)

        def callback(userid, request):
            return None

        policy = self._makeOne(userid='fred', callback=callback)
        self.assertEqual(policy.authenticated_userid(request), None)
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            'tests.test_authentication.MyAuthenticationPolicy.'
            'authenticated_userid: groupfinder callback returned None; '
            'returning None',
        )

    def test_authenticated_userid_with_callback_success(self):
        request = DummyRequest(registry=self.config.registry)

        def callback(userid, request):
            return []

        policy = self._makeOne(userid='fred', callback=callback)
        self.assertEqual(policy.authenticated_userid(request), 'fred')
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            "tests.test_authentication.MyAuthenticationPolicy."
            "authenticated_userid: groupfinder callback returned []; "
            "returning 'fred'",
        )

    def test_authenticated_userid_fails_cleaning_as_Authenticated(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne(userid='system.Authenticated')
        self.assertEqual(policy.authenticated_userid(request), None)
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            "tests.test_authentication.MyAuthenticationPolicy."
            "authenticated_userid: use of userid 'system.Authenticated' is "
            "disallowed by any built-in Pyramid security policy, returning "
            "None",
        )

    def test_authenticated_userid_fails_cleaning_as_Everyone(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne(userid='system.Everyone')
        self.assertEqual(policy.authenticated_userid(request), None)
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            "tests.test_authentication.MyAuthenticationPolicy."
            "authenticated_userid: use of userid 'system.Everyone' is "
            "disallowed by any built-in Pyramid security policy, returning "
            "None",
        )

    def test_effective_principals_no_unauthenticated_userid(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne()
        self.assertEqual(
            policy.effective_principals(request), ['system.Everyone']
        )
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            "tests.test_authentication.MyAuthenticationPolicy."
            "effective_principals: unauthenticated_userid returned None; "
            "returning ['system.Everyone']",
        )

    def test_effective_principals_no_callback(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne(userid='fred')
        self.assertEqual(
            policy.effective_principals(request),
            ['system.Everyone', 'system.Authenticated', 'fred'],
        )
        self.assertEqual(len(self.messages), 2)
        self.assertEqual(
            self.messages[0],
            'tests.test_authentication.MyAuthenticationPolicy.'
            'effective_principals: groupfinder callback is None, so groups '
            'is []',
        )
        self.assertEqual(
            self.messages[1],
            "tests.test_authentication.MyAuthenticationPolicy."
            "effective_principals: returning effective principals: "
            "['system.Everyone', 'system.Authenticated', 'fred']",
        )

    def test_effective_principals_with_callback_fail(self):
        request = DummyRequest(registry=self.config.registry)

        def callback(userid, request):
            return None

        policy = self._makeOne(userid='fred', callback=callback)
        self.assertEqual(
            policy.effective_principals(request), ['system.Everyone']
        )
        self.assertEqual(len(self.messages), 2)
        self.assertEqual(
            self.messages[0],
            'tests.test_authentication.MyAuthenticationPolicy.'
            'effective_principals: groupfinder callback returned None as '
            'groups',
        )
        self.assertEqual(
            self.messages[1],
            "tests.test_authentication.MyAuthenticationPolicy."
            "effective_principals: returning effective principals: "
            "['system.Everyone']",
        )

    def test_effective_principals_with_callback_success(self):
        request = DummyRequest(registry=self.config.registry)

        def callback(userid, request):
            return []

        policy = self._makeOne(userid='fred', callback=callback)
        self.assertEqual(
            policy.effective_principals(request),
            ['system.Everyone', 'system.Authenticated', 'fred'],
        )
        self.assertEqual(len(self.messages), 2)
        self.assertEqual(
            self.messages[0],
            'tests.test_authentication.MyAuthenticationPolicy.'
            'effective_principals: groupfinder callback returned [] as groups',
        )
        self.assertEqual(
            self.messages[1],
            "tests.test_authentication.MyAuthenticationPolicy."
            "effective_principals: returning effective principals: "
            "['system.Everyone', 'system.Authenticated', 'fred']",
        )

    def test_effective_principals_with_unclean_principal_Authenticated(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne(userid='system.Authenticated')
        self.assertEqual(
            policy.effective_principals(request), ['system.Everyone']
        )
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            "tests.test_authentication.MyAuthenticationPolicy."
            "effective_principals: unauthenticated_userid returned disallowed "
            "'system.Authenticated'; returning ['system.Everyone'] as if it "
            "was None",
        )

    def test_effective_principals_with_unclean_principal_Everyone(self):
        request = DummyRequest(registry=self.config.registry)
        policy = self._makeOne(userid='system.Everyone')
        self.assertEqual(
            policy.effective_principals(request), ['system.Everyone']
        )
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(
            self.messages[0],
            "tests.test_authentication.MyAuthenticationPolicy."
            "effective_principals: unauthenticated_userid returned disallowed "
            "'system.Everyone'; returning ['system.Everyone'] as if it "
            "was None",
        )


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
            {'repoze.who.identity': {'repoze.who.userid': 'fred'}}
        )
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), 'fred')

    def test_authenticated_userid_None(self):
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid(self):
        request = DummyRequest(
            {'repoze.who.identity': {'repoze.who.userid': 'fred'}}
        )
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), 'fred')

    def test_authenticated_userid_repoze_who_userid_is_None(self):
        request = DummyRequest(
            {'repoze.who.identity': {'repoze.who.userid': None}}
        )
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid_with_callback_returns_None(self):
        request = DummyRequest(
            {'repoze.who.identity': {'repoze.who.userid': 'fred'}}
        )

        def callback(identity, request):
            return None

        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid_with_callback_returns_something(self):
        request = DummyRequest(
            {'repoze.who.identity': {'repoze.who.userid': 'fred'}}
        )

        def callback(identity, request):
            return ['agroup']

        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.authenticated_userid(request), 'fred')

    def test_authenticated_userid_unclean_principal_Authenticated(self):
        request = DummyRequest(
            {
                'repoze.who.identity': {
                    'repoze.who.userid': 'system.Authenticated'
                }
            }
        )
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid_unclean_principal_Everyone(self):
        request = DummyRequest(
            {'repoze.who.identity': {'repoze.who.userid': 'system.Everyone'}}
        )
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_effective_principals_None(self):
        from pyramid.security import Everyone

        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_userid_only(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated

        request = DummyRequest(
            {'repoze.who.identity': {'repoze.who.userid': 'fred'}}
        )
        policy = self._makeOne()
        self.assertEqual(
            policy.effective_principals(request),
            [Everyone, Authenticated, 'fred'],
        )

    def test_effective_principals_userid_and_groups(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated

        request = DummyRequest(
            {
                'repoze.who.identity': {
                    'repoze.who.userid': 'fred',
                    'groups': ['quux', 'biz'],
                }
            }
        )

        def callback(identity, request):
            return identity['groups']

        policy = self._makeOne(callback=callback)
        self.assertEqual(
            policy.effective_principals(request),
            [Everyone, Authenticated, 'fred', 'quux', 'biz'],
        )

    def test_effective_principals_userid_callback_returns_None(self):
        from pyramid.security import Everyone

        request = DummyRequest(
            {
                'repoze.who.identity': {
                    'repoze.who.userid': 'fred',
                    'groups': ['quux', 'biz'],
                }
            }
        )

        def callback(identity, request):
            return None

        policy = self._makeOne(callback=callback)
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_repoze_who_userid_is_None(self):
        from pyramid.security import Everyone

        request = DummyRequest(
            {'repoze.who.identity': {'repoze.who.userid': None}}
        )
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_repoze_who_userid_is_unclean_Everyone(self):
        from pyramid.security import Everyone

        request = DummyRequest(
            {'repoze.who.identity': {'repoze.who.userid': 'system.Everyone'}}
        )
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_repoze_who_userid_is_unclean_Authenticated(
        self
    ):
        from pyramid.security import Everyone

        request = DummyRequest(
            {
                'repoze.who.identity': {
                    'repoze.who.userid': 'system.Authenticated'
                }
            }
        )
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_remember_no_plugins(self):
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.remember(request, 'fred')
        self.assertEqual(result, [])

    def test_remember(self):
        authtkt = DummyWhoPlugin()
        request = DummyRequest({'repoze.who.plugins': {'auth_tkt': authtkt}})
        policy = self._makeOne()
        result = policy.remember(request, 'fred')
        self.assertEqual(result[0], request.environ)
        self.assertEqual(result[1], {'repoze.who.userid': 'fred'})

    def test_remember_kwargs(self):
        authtkt = DummyWhoPlugin()
        request = DummyRequest({'repoze.who.plugins': {'auth_tkt': authtkt}})
        policy = self._makeOne()
        result = policy.remember(request, 'fred', max_age=23)
        self.assertEqual(
            result[1], {'repoze.who.userid': 'fred', 'max_age': 23}
        )

    def test_forget_no_plugins(self):
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.forget(request)
        self.assertEqual(result, [])

    def test_forget(self):
        authtkt = DummyWhoPlugin()
        request = DummyRequest(
            {
                'repoze.who.plugins': {'auth_tkt': authtkt},
                'repoze.who.identity': {'repoze.who.userid': 'fred'},
            }
        )
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
        request = DummyRequest({'REMOTE_USER': 'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), 'fred')

    def test_authenticated_userid_None(self):
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid(self):
        request = DummyRequest({'REMOTE_USER': 'fred'})
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

        request = DummyRequest({'REMOTE_USER': 'fred'})
        policy = self._makeOne()
        self.assertEqual(
            policy.effective_principals(request),
            [Everyone, Authenticated, 'fred'],
        )

    def test_remember(self):
        request = DummyRequest({'REMOTE_USER': 'fred'})
        policy = self._makeOne()
        result = policy.remember(request, 'fred')
        self.assertEqual(result, [])

    def test_forget(self):
        request = DummyRequest({'REMOTE_USER': 'fred'})
        policy = self._makeOne()
        result = policy.forget(request)
        self.assertEqual(result, [])


class TestAuthTktAuthenticationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.authentication import AuthTktAuthenticationPolicy

        return AuthTktAuthenticationPolicy

    def _makeOne(self, callback, cookieidentity, **kw):
        inst = self._getTargetClass()('secret', callback, **kw)
        inst.cookie = DummyCookieHelper(cookieidentity)
        return inst

    def setUp(self):
        self.warnings = warnings.catch_warnings()
        self.warnings.__enter__()
        warnings.simplefilter('ignore', DeprecationWarning)

    def tearDown(self):
        self.warnings.__exit__(None, None, None)

    def test_allargs(self):
        # pass all known args
        inst = self._getTargetClass()(
            'secret',
            callback=None,
            cookie_name=None,
            secure=False,
            include_ip=False,
            timeout=None,
            reissue_time=None,
            hashalg='sha512',
            samesite=None,
        )
        self.assertEqual(inst.callback, None)

    def test_hashalg_override(self):
        # important to ensure hashalg is passed to cookie helper
        inst = self._getTargetClass()('secret', hashalg='sha512')
        self.assertEqual(inst.cookie.hashalg, 'sha512')

    def test_unauthenticated_userid_returns_None(self):
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid(self):
        request = DummyRequest({'REMOTE_USER': 'fred'})
        policy = self._makeOne(None, {'userid': 'fred'})
        self.assertEqual(policy.unauthenticated_userid(request), 'fred')

    def test_authenticated_userid_no_cookie_identity(self):
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid_callback_returns_None(self):
        request = DummyRequest({})

        def callback(userid, request):
            return None

        policy = self._makeOne(callback, {'userid': 'fred'})
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid(self):
        request = DummyRequest({})

        def callback(userid, request):
            return True

        policy = self._makeOne(callback, {'userid': 'fred'})
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

        policy = self._makeOne(callback, {'userid': 'fred'})
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated

        request = DummyRequest({})

        def callback(userid, request):
            return ['group.foo']

        policy = self._makeOne(callback, {'userid': 'fred'})
        self.assertEqual(
            policy.effective_principals(request),
            [Everyone, Authenticated, 'fred', 'group.foo'],
        )

    def test_remember(self):
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        result = policy.remember(request, 'fred')
        self.assertEqual(result, [])

    def test_remember_with_extra_kargs(self):
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        result = policy.remember(request, 'fred', a=1, b=2)
        self.assertEqual(policy.cookie.kw, {'a': 1, 'b': 2})
        self.assertEqual(result, [])

    def test_forget(self):
        request = DummyRequest({})
        policy = self._makeOne(None, None)
        result = policy.forget(request)
        self.assertEqual(result, [])

    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthenticationPolicy

        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IAuthenticationPolicy

        verifyObject(IAuthenticationPolicy, self._makeOne(None, None))


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
        request = DummyRequest(session={'userid': 'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), 'fred')

    def test_authenticated_userid_no_cookie_identity(self):
        request = DummyRequest()
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid_callback_returns_None(self):
        request = DummyRequest(session={'userid': 'fred'})

        def callback(userid, request):
            return None

        policy = self._makeOne(callback)
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid(self):
        request = DummyRequest(session={'userid': 'fred'})

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

        request = DummyRequest(session={'userid': 'fred'})

        def callback(userid, request):
            return None

        policy = self._makeOne(callback)
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated

        request = DummyRequest(session={'userid': 'fred'})

        def callback(userid, request):
            return ['group.foo']

        policy = self._makeOne(callback)
        self.assertEqual(
            policy.effective_principals(request),
            [Everyone, Authenticated, 'fred', 'group.foo'],
        )

    def test_remember(self):
        request = DummyRequest()
        policy = self._makeOne()
        result = policy.remember(request, 'fred')
        self.assertEqual(request.session.get('userid'), 'fred')
        self.assertEqual(result, [])

    def test_forget(self):
        request = DummyRequest(session={'userid': 'fred'})
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


class TestBasicAuthAuthenticationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.authentication import BasicAuthAuthenticationPolicy as cls

        return cls

    def _makeOne(self, check):
        return self._getTargetClass()(check, realm='SomeRealm')

    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthenticationPolicy

        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_unauthenticated_userid(self):
        import base64

        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            bytes_('chrisr:password')
        ).decode('ascii')
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), 'chrisr')

    def test_unauthenticated_userid_no_credentials(self):
        request = testing.DummyRequest()
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_bad_header(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = '...'
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid_not_basic(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Complicated things'
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid_corrupt_base64(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic chrisr:password'
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_authenticated_userid(self):
        import base64

        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            bytes_('chrisr:password')
        ).decode('ascii')

        def check(username, password, request):
            return []

        policy = self._makeOne(check)
        self.assertEqual(policy.authenticated_userid(request), 'chrisr')

    def test_authenticated_userid_utf8(self):
        import base64

        request = testing.DummyRequest()
        inputs = (
            b'm\xc3\xb6rk\xc3\xb6:' b'm\xc3\xb6rk\xc3\xb6password'
        ).decode('utf-8')
        request.headers['Authorization'] = 'Basic %s' % (
            base64.b64encode(inputs.encode('utf-8')).decode('latin-1')
        )

        def check(username, password, request):
            return []

        policy = self._makeOne(check)
        self.assertEqual(
            policy.authenticated_userid(request),
            b'm\xc3\xb6rk\xc3\xb6'.decode('utf-8'),
        )

    def test_authenticated_userid_latin1(self):
        import base64

        request = testing.DummyRequest()
        inputs = (
            b'm\xc3\xb6rk\xc3\xb6:' b'm\xc3\xb6rk\xc3\xb6password'
        ).decode('utf-8')
        request.headers['Authorization'] = 'Basic %s' % (
            base64.b64encode(inputs.encode('latin-1')).decode('latin-1')
        )

        def check(username, password, request):
            return []

        policy = self._makeOne(check)
        self.assertEqual(
            policy.authenticated_userid(request),
            b'm\xc3\xb6rk\xc3\xb6'.decode('utf-8'),
        )

    def test_unauthenticated_userid_invalid_payload(self):
        import base64

        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            bytes_('chrisrpassword')
        ).decode('ascii')
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_remember(self):
        policy = self._makeOne(None)
        self.assertEqual(policy.remember(None, None), [])

    def test_forget(self):
        policy = self._makeOne(None)
        self.assertEqual(
            policy.forget(None),
            [('WWW-Authenticate', 'Basic realm="SomeRealm"')],
        )


class TestExtractHTTPBasicCredentials(unittest.TestCase):
    def _get_func(self):
        from pyramid.authentication import extract_http_basic_credentials

        return extract_http_basic_credentials

    def test_no_auth_header(self):
        request = testing.DummyRequest()
        fn = self._get_func()

        self.assertIsNone(fn(request))

    def test_invalid_payload(self):
        import base64

        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            bytes_('chrisrpassword')
        ).decode('ascii')
        fn = self._get_func()
        self.assertIsNone(fn(request))

    def test_not_a_basic_auth_scheme(self):
        import base64

        request = testing.DummyRequest()
        request.headers['Authorization'] = 'OtherScheme %s' % base64.b64encode(
            bytes_('chrisr:password')
        ).decode('ascii')
        fn = self._get_func()
        self.assertIsNone(fn(request))

    def test_no_base64_encoding(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic ...'
        fn = self._get_func()
        self.assertIsNone(fn(request))

    def test_latin1_payload(self):
        import base64

        request = testing.DummyRequest()
        inputs = (
            b'm\xc3\xb6rk\xc3\xb6:' b'm\xc3\xb6rk\xc3\xb6password'
        ).decode('utf-8')
        request.headers['Authorization'] = 'Basic %s' % (
            base64.b64encode(inputs.encode('latin-1')).decode('latin-1')
        )
        fn = self._get_func()
        self.assertEqual(
            fn(request),
            (
                b'm\xc3\xb6rk\xc3\xb6'.decode('utf-8'),
                b'm\xc3\xb6rk\xc3\xb6password'.decode('utf-8'),
            ),
        )

    def test_utf8_payload(self):
        import base64

        request = testing.DummyRequest()
        inputs = (
            b'm\xc3\xb6rk\xc3\xb6:' b'm\xc3\xb6rk\xc3\xb6password'
        ).decode('utf-8')
        request.headers['Authorization'] = 'Basic %s' % (
            base64.b64encode(inputs.encode('utf-8')).decode('latin-1')
        )
        fn = self._get_func()
        self.assertEqual(
            fn(request),
            (
                b'm\xc3\xb6rk\xc3\xb6'.decode('utf-8'),
                b'm\xc3\xb6rk\xc3\xb6password'.decode('utf-8'),
            ),
        )

    def test_namedtuple_return(self):
        import base64

        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            bytes_('chrisr:pass')
        ).decode('ascii')
        fn = self._get_func()
        result = fn(request)

        self.assertEqual(result.username, 'chrisr')
        self.assertEqual(result.password, 'pass')


class DummyContext:
    pass


class DummyRequest:
    domain = 'localhost'

    def __init__(self, environ=None, session=None, registry=None, cookie=None):
        self.environ = environ or {}
        self.session = session or {}
        self.registry = registry
        self.callbacks = []


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
