import unittest

from pyramid import testing


class TestAllPermissionsList(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTargetClass(self):
        from pyramid.security import AllPermissionsList

        return AllPermissionsList

    def _makeOne(self):
        return self._getTargetClass()()

    def test_equality_w_self(self):
        thing = self._makeOne()
        self.assertTrue(thing.__eq__(thing))

    def test_equality_w_other_instances_of_class(self):
        thing = self._makeOne()
        other = self._makeOne()
        self.assertTrue(thing.__eq__(other))

    def test_equality_miss(self):
        thing = self._makeOne()
        other = object()
        self.assertFalse(thing.__eq__(other))

    def test_contains_w_string(self):
        thing = self._makeOne()
        self.assertTrue('anything' in thing)

    def test_contains_w_object(self):
        thing = self._makeOne()
        self.assertTrue(object() in thing)

    def test_iterable(self):
        thing = self._makeOne()
        self.assertEqual(list(thing), [])

    def test_singleton(self):
        from pyramid.security import ALL_PERMISSIONS

        self.assertEqual(ALL_PERMISSIONS.__class__, self._getTargetClass())


class TestAllowed(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.security import Allowed

        return Allowed

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_it(self):
        allowed = self._makeOne('hello')
        self.assertEqual(allowed.msg, 'hello')
        self.assertEqual(allowed, True)
        self.assertTrue(allowed)
        self.assertEqual(str(allowed), 'hello')
        self.assertTrue('<Allowed instance at ' in repr(allowed))
        self.assertTrue("with msg 'hello'>" in repr(allowed))


class TestDenied(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.security import Denied

        return Denied

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_it(self):
        denied = self._makeOne('hello')
        self.assertEqual(denied.msg, 'hello')
        self.assertEqual(denied, False)
        self.assertFalse(denied)
        self.assertEqual(str(denied), 'hello')
        self.assertTrue('<Denied instance at ' in repr(denied))
        self.assertTrue("with msg 'hello'>" in repr(denied))


class TestACLAllowed(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.security import ACLAllowed

        return ACLAllowed

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_it(self):
        from pyramid.security import Allowed

        msg = (
            "ACLAllowed permission 'permission' via ACE 'ace' in ACL 'acl' "
            "on context 'ctx' for principals 'principals'"
        )
        allowed = self._makeOne(
            'ace', 'acl', 'permission', 'principals', 'ctx'
        )
        self.assertIsInstance(allowed, Allowed)
        self.assertTrue(msg in allowed.msg)
        self.assertEqual(allowed, True)
        self.assertTrue(allowed)
        self.assertEqual(str(allowed), msg)
        self.assertTrue('<ACLAllowed instance at ' in repr(allowed))
        self.assertTrue("with msg %r>" % msg in repr(allowed))


class TestACLDenied(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.security import ACLDenied

        return ACLDenied

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_it(self):
        from pyramid.security import Denied

        msg = (
            "ACLDenied permission 'permission' via ACE 'ace' in ACL 'acl' "
            "on context 'ctx' for principals 'principals'"
        )
        denied = self._makeOne('ace', 'acl', 'permission', 'principals', 'ctx')
        self.assertIsInstance(denied, Denied)
        self.assertTrue(msg in denied.msg)
        self.assertEqual(denied, False)
        self.assertFalse(denied)
        self.assertEqual(str(denied), msg)
        self.assertTrue('<ACLDenied instance at ' in repr(denied))
        self.assertTrue("with msg %r>" % msg in repr(denied))


class TestPrincipalsAllowedByPermission(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg):
        from pyramid.security import principals_allowed_by_permission

        return principals_allowed_by_permission(*arg)

    def test_no_authorization_policy(self):
        from pyramid.security import Everyone

        context = DummyContext()
        result = self._callFUT(context, 'view')
        self.assertEqual(result, [Everyone])

    def test_with_authorization_policy(self):
        from pyramid.threadlocal import get_current_registry

        registry = get_current_registry()
        _registerAuthorizationPolicy(registry, 'yo')
        context = DummyContext()
        result = self._callFUT(context, 'view')
        self.assertEqual(result, 'yo')


class TestRemember(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kwarg):
        from pyramid.security import remember

        return remember(*arg, **kwarg)

    def test_no_security_policy(self):
        request = _makeRequest()
        result = self._callFUT(request, 'me')
        self.assertEqual(result, [])

    def test_with_security_policy(self):
        request = _makeRequest()
        registry = request.registry
        _registerSecurityPolicy(registry, 'yo')
        result = self._callFUT(request, 'me')
        self.assertEqual(result, [('X-Pyramid-Test', 'me')])

    def test_with_missing_arg(self):
        request = _makeRequest()
        registry = request.registry
        _registerSecurityPolicy(registry, 'yo')
        self.assertRaises(TypeError, lambda: self._callFUT(request))


class TestForget(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg):
        from pyramid.security import forget

        return forget(*arg)

    def test_no_security_policy(self):
        request = _makeRequest()
        result = self._callFUT(request)
        self.assertEqual(result, [])

    def test_with_security_policy(self):
        request = _makeRequest()
        _registerSecurityPolicy(request.registry, 'yo')
        result = self._callFUT(request)
        self.assertEqual(result, [('X-Pyramid-Test', 'logout')])


class TestViewExecutionPermitted(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.security import view_execution_permitted

        return view_execution_permitted(*arg, **kw)

    def _registerSecuredView(self, view_name, allow=True):
        from zope.interface import Interface

        from pyramid.interfaces import ISecuredView, IViewClassifier
        from pyramid.threadlocal import get_current_registry

        class Checker:
            def __permitted__(self, context, request):
                self.context = context
                self.request = request
                return allow

        checker = Checker()
        reg = get_current_registry()
        reg.registerAdapter(
            checker,
            (IViewClassifier, Interface, Interface),
            ISecuredView,
            view_name,
        )
        return checker

    def test_no_permission(self):
        from zope.interface import Interface

        from pyramid.interfaces import ISettings, IView, IViewClassifier
        from pyramid.threadlocal import get_current_registry

        settings = dict(debug_authorization=True)
        reg = get_current_registry()
        reg.registerUtility(settings, ISettings)
        context = DummyContext()
        request = testing.DummyRequest({})

        class DummyView:
            pass

        view = DummyView()
        reg.registerAdapter(
            view, (IViewClassifier, Interface, Interface), IView, ''
        )
        result = self._callFUT(context, request, '')
        msg = result.msg
        self.assertTrue("Allowed: view name '' in context" in msg)
        self.assertTrue('(no permission defined)' in msg)
        self.assertEqual(result, True)

    def test_no_view_registered(self):
        from pyramid.interfaces import ISettings
        from pyramid.threadlocal import get_current_registry

        settings = dict(debug_authorization=True)
        reg = get_current_registry()
        reg.registerUtility(settings, ISettings)
        context = DummyContext()
        request = testing.DummyRequest({})
        self.assertRaises(TypeError, self._callFUT, context, request, '')

    def test_with_permission(self):
        from zope.interface import Interface, directlyProvides

        from pyramid.interfaces import IRequest

        class IContext(Interface):
            pass

        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerSecuredView('', True)
        request = testing.DummyRequest({})
        directlyProvides(request, IRequest)
        result = self._callFUT(context, request, '')
        self.assertTrue(result)


class TestIdentity(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_identity_no_security_policy(self):
        request = _makeRequest()
        self.assertEqual(request.identity, None)

    def test_identity(self):
        request = _makeRequest()
        _registerSecurityPolicy(request.registry, 'yo')
        self.assertEqual(request.identity, 'yo')


class TestAuthenticatedUserId(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_no_authentication_policy(self):
        request = _makeRequest()
        self.assertEqual(request.authenticated_userid, None)

    def test_with_security_policy(self):
        request = _makeRequest()
        _registerSecurityPolicy(request.registry, '123')
        self.assertEqual(request.authenticated_userid, '123')

    def test_with_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        _registerLegacySecurityPolicy(request.registry)
        self.assertEqual(request.authenticated_userid, 'yo')

    def test_security_policy_trumps_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        _registerSecurityPolicy(request.registry, 'wat')
        self.assertEqual(request.authenticated_userid, 'wat')


class TestUnAuthenticatedUserId(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_no_authentication_policy(self):
        request = _makeRequest()
        self.assertEqual(request.unauthenticated_userid, None)

    def test_with_security_policy(self):
        request = _makeRequest()
        _registerSecurityPolicy(request.registry, 'yo')
        self.assertEqual(request.unauthenticated_userid, 'yo')

    def test_legacy_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        _registerLegacySecurityPolicy(request.registry)
        self.assertEqual(request.unauthenticated_userid, 'yo')

    def test_security_policy_trumps_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        _registerSecurityPolicy(request.registry, 'wat')
        self.assertEqual(request.unauthenticated_userid, 'wat')


class TestIsAuthenticated(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_no_security_policy(self):
        request = _makeRequest()
        self.assertIs(request.is_authenticated, False)

    def test_with_security_policy(self):
        request = _makeRequest()
        _registerSecurityPolicy(request.registry, '123')
        self.assertIs(request.is_authenticated, True)

    def test_with_legacy_security_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        _registerLegacySecurityPolicy(request.registry)
        self.assertEqual(request.authenticated_userid, 'yo')


class TestEffectivePrincipals(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_no_authentication_policy(self):
        from pyramid.security import Everyone

        request = _makeRequest()
        self.assertEqual(request.effective_principals, [Everyone])

    def test_with_security_policy(self):
        from pyramid.security import Everyone

        request = _makeRequest()
        _registerSecurityPolicy(request.registry, 'yo')
        self.assertEqual(request.effective_principals, [Everyone])

    def test_legacy_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        _registerLegacySecurityPolicy(request.registry)
        self.assertEqual(request.effective_principals, 'yo')

    def test_security_policy_trumps_authentication_policy(self):
        from pyramid.security import Everyone

        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'wat')
        _registerSecurityPolicy(request.registry, 'yo')
        self.assertEqual(request.effective_principals, [Everyone])


class TestHasPermission(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self):
        from pyramid.registry import Registry
        from pyramid.security import SecurityAPIMixin

        mixin = SecurityAPIMixin()
        mixin.registry = Registry()
        mixin.context = object()
        return mixin

    def test_no_security_policy(self):
        request = self._makeOne()
        result = request.has_permission('view')
        self.assertTrue(result)
        self.assertEqual(result.msg, 'No security policy in use.')

    def test_with_security_registered(self):
        request = self._makeOne()
        _registerSecurityPolicy(request.registry, 'yo')
        self.assertEqual(request.has_permission('view', context=None), 'yo')

    def test_with_no_context_passed(self):
        request = self._makeOne()
        self.assertTrue(request.has_permission('view'))

    def test_with_no_context_passed_or_on_request(self):
        request = self._makeOne()
        del request.context
        self.assertRaises(AttributeError, request.has_permission, 'view')


class TestLegacySecurityPolicy(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_identity(self):
        from pyramid.security import LegacySecurityPolicy

        request = _makeRequest()
        policy = LegacySecurityPolicy()
        _registerAuthenticationPolicy(request.registry, 'userid')

        self.assertEqual(policy.identity(request), 'userid')

    def test_remember(self):
        from pyramid.security import LegacySecurityPolicy

        request = _makeRequest()
        policy = LegacySecurityPolicy()
        _registerAuthenticationPolicy(request.registry, None)

        self.assertEqual(
            policy.remember(request, 'userid'), [('X-Pyramid-Test', 'userid')]
        )

    def test_forget(self):
        from pyramid.security import LegacySecurityPolicy

        request = _makeRequest()
        policy = LegacySecurityPolicy()
        _registerAuthenticationPolicy(request.registry, None)

        self.assertEqual(
            policy.forget(request), [('X-Pyramid-Test', 'logout')]
        )

    def test_forget_with_kwargs(self):
        from pyramid.security import LegacySecurityPolicy

        policy = LegacySecurityPolicy()
        self.assertRaises(ValueError, lambda: policy.forget(None, foo='bar'))

    def test_permits(self):
        from pyramid.security import LegacySecurityPolicy

        request = _makeRequest()
        policy = LegacySecurityPolicy()
        _registerAuthenticationPolicy(request.registry, ['p1', 'p2'])
        _registerAuthorizationPolicy(request.registry, True)

        self.assertTrue(policy.permits(request, request.context, 'permission'))


_TEST_HEADER = 'X-Pyramid-Test'


class DummyContext:
    def __init__(self, *arg, **kw):
        self.__dict__.update(kw)


class DummySecurityPolicy:
    def __init__(self, result):
        self.result = result

    def identity(self, request):
        return self.result

    def authenticated_userid(self, request):
        return self.result

    def permits(self, request, context, permission):
        return self.result

    def remember(self, request, userid, **kw):
        headers = [(_TEST_HEADER, userid)]
        self._header_remembered = headers[0]
        return headers

    def forget(self, request, **kw):
        headers = [(_TEST_HEADER, 'logout')]
        self._header_forgotten = headers[0]
        return headers


class DummyAuthenticationPolicy:
    def __init__(self, result):
        self.result = result

    def effective_principals(self, request):
        return self.result

    def unauthenticated_userid(self, request):
        return self.result

    def authenticated_userid(self, request):
        return self.result

    def remember(self, request, userid, **kw):
        headers = [(_TEST_HEADER, userid)]
        self._header_remembered = headers[0]
        return headers

    def forget(self, request):
        headers = [(_TEST_HEADER, 'logout')]
        self._header_forgotten = headers[0]
        return headers


class DummyAuthorizationPolicy:
    def __init__(self, result):
        self.result = result

    def permits(self, context, principals, permission):
        return self.result

    def principals_allowed_by_permission(self, context, permission):
        return self.result


def _registerSecurityPolicy(reg, result):
    from pyramid.interfaces import ISecurityPolicy

    policy = DummySecurityPolicy(result)
    reg.registerUtility(policy, ISecurityPolicy)
    return policy


def _registerLegacySecurityPolicy(reg):
    from pyramid.interfaces import ISecurityPolicy
    from pyramid.security import LegacySecurityPolicy

    policy = LegacySecurityPolicy()
    reg.registerUtility(policy, ISecurityPolicy)
    return policy


def _registerAuthenticationPolicy(reg, result):
    from pyramid.interfaces import IAuthenticationPolicy

    policy = DummyAuthenticationPolicy(result)
    reg.registerUtility(policy, IAuthenticationPolicy)
    return policy


def _registerAuthorizationPolicy(reg, result):
    from pyramid.interfaces import IAuthorizationPolicy

    policy = DummyAuthorizationPolicy(result)
    reg.registerUtility(policy, IAuthorizationPolicy)
    return policy


def _makeRequest():
    from pyramid.registry import Registry

    request = testing.DummyRequest(environ={})
    request.registry = Registry()
    request.context = object()
    return request
