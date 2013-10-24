import unittest

from pyramid.testing import cleanUp, DummyRequest

_TEST_HEADER = 'X-Pyramid-Test'

class TestAllPermissionsList(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from pyramid.security import AllPermissionsList
        return AllPermissionsList

    def _makeOne(self):
        return self._getTargetClass()()

    def test_it(self):
        thing = self._makeOne()
        self.assertTrue(thing.__eq__(thing))
        self.assertEqual(thing.__iter__(), ())
        self.assertTrue('anything' in thing)

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
        msg = ("ACLAllowed permission 'permission' via ACE 'ace' in ACL 'acl' "
               "on context 'ctx' for principals 'principals'")
        allowed = self._makeOne('ace', 'acl', 'permission', 'principals', 'ctx')
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
        msg = ("ACLDenied permission 'permission' via ACE 'ace' in ACL 'acl' "
               "on context 'ctx' for principals 'principals'")
        denied = self._makeOne('ace', 'acl', 'permission', 'principals', 'ctx')
        self.assertTrue(msg in denied.msg)
        self.assertEqual(denied, False)
        self.assertFalse(denied)
        self.assertEqual(str(denied), msg)
        self.assertTrue('<ACLDenied instance at ' in repr(denied))
        self.assertTrue("with msg %r>" % msg in repr(denied))

class TestPrincipalsAllowedByPermission(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

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

class TestViewExecutionPermitted(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

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

class TestViewExecutionPermitted(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
    
    def _callFUT(self, *arg, **kw):
        from pyramid.security import view_execution_permitted
        return view_execution_permitted(*arg, **kw)

    def _registerSecuredView(self, view_name, allow=True):
        from pyramid.threadlocal import get_current_registry
        from zope.interface import Interface
        from pyramid.interfaces import ISecuredView
        from pyramid.interfaces import IViewClassifier
        class Checker(object):
            def __permitted__(self, context, request):
                self.context = context
                self.request = request
                return allow
        checker = Checker()
        reg = get_current_registry()
        reg.registerAdapter(checker, (IViewClassifier, Interface, Interface),
                            ISecuredView, view_name)
        return checker

    def test_no_permission(self):
        from zope.interface import Interface
        from pyramid.threadlocal import get_current_registry
        from pyramid.interfaces import ISettings
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        settings = dict(debug_authorization=True)
        reg = get_current_registry()
        reg.registerUtility(settings, ISettings)
        context = DummyContext()
        request = DummyRequest({})
        class DummyView(object):
            pass
        view = DummyView()
        reg.registerAdapter(view, (IViewClassifier, Interface, Interface),
                            IView, '')
        result = self._callFUT(context, request, '')
        msg = result.msg
        self.assertTrue("Allowed: view name '' in context" in msg)
        self.assertTrue('(no permission defined)' in msg)
        self.assertEqual(result, True)

    def test_no_view_registered(self):
        from pyramid.threadlocal import get_current_registry
        from pyramid.interfaces import ISettings
        settings = dict(debug_authorization=True)
        reg = get_current_registry()
        reg.registerUtility(settings, ISettings)
        context = DummyContext()
        request = DummyRequest({})
        self.assertRaises(TypeError, self._callFUT, context, request, '')

    def test_with_permission(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from pyramid.interfaces import IRequest
        class IContext(Interface):
            pass
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerSecuredView('', True)
        request = DummyRequest({})
        directlyProvides(request, IRequest)
        result = self._callFUT(context, request, '')
        self.assertTrue(result)

class AuthenticationAPIMixinTest(object):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self):
        from pyramid.registry import Registry
        from pyramid.security import AuthenticationAPIMixin
        request = DummyRequest(environ={})
        self.assertTrue(isinstance(request, AuthenticationAPIMixin))
        request.registry = Registry()
        request.context = object()
        return request

    def _makeFakeOne(self):
        def fake_proxied_method(method):
            def proxy(*args, **kw):
                return method.__name__
            return proxy

        def fake_proxied_property(method):
            return property(fget=lambda req: method.__name__)

        class FakeRequest(DummyRequest):
            @fake_proxied_property
            def authenticated_userid(req):
                pass

            @fake_proxied_property
            def unauthenticated_userid(req):
                pass

            @fake_proxied_property
            def effective_principals(req):
                pass

            @fake_proxied_method
            def forget_userid(req):
                pass

            @fake_proxied_method
            def remember_userid(req, principal, **kw):
                pass

        return FakeRequest({})

class TestAuthenticatedUserId(AuthenticationAPIMixinTest, unittest.TestCase):
    def test_backward_compat_delegates_to_mixin(self):
        request = self._makeFakeOne()
        from pyramid.security import authenticated_userid
        self.assertEqual(authenticated_userid(request), 'authenticated_userid')

    def test_no_authentication_policy(self):
        request = self._makeOne()
        self.assertEqual(request.authenticated_userid, None)

    def test_with_authentication_policy(self):
        request = self._makeOne()
        _registerAuthenticationPolicy(request.registry, 'yo')
        self.assertEqual(request.authenticated_userid, 'yo')

    def test_with_authentication_policy_no_reg_on_request(self):
        from pyramid.threadlocal import get_current_registry
        registry = get_current_registry()
        request = self._makeOne()
        del request.registry
        _registerAuthenticationPolicy(registry, 'yo')
        self.assertEqual(request.authenticated_userid, 'yo')

class TestUnAuthenticatedUserId(AuthenticationAPIMixinTest, unittest.TestCase):
    def test_backward_compat_delegates_to_mixin(self):
        request = self._makeFakeOne()
        from pyramid.security import unauthenticated_userid
        self.assertEqual(unauthenticated_userid(request),
                         'unauthenticated_userid')

    def test_no_authentication_policy(self):
        request = self._makeOne()
        self.assertEqual(request.unauthenticated_userid, None)

    def test_with_authentication_policy(self):
        request = self._makeOne()
        _registerAuthenticationPolicy(request.registry, 'yo')
        self.assertEqual(request.unauthenticated_userid, 'yo')

    def test_with_authentication_policy_no_reg_on_request(self):
        from pyramid.threadlocal import get_current_registry
        registry = get_current_registry()
        request = self._makeOne()
        del request.registry
        _registerAuthenticationPolicy(registry, 'yo')
        self.assertEqual(request.unauthenticated_userid, 'yo')

class TestEffectivePrincipals(AuthenticationAPIMixinTest, unittest.TestCase):
    def test_backward_compat_delegates_to_mixin(self):
        request = self._makeFakeOne()
        from pyramid.security import effective_principals
        self.assertEqual(effective_principals(request), 'effective_principals')

    def test_no_authentication_policy(self):
        from pyramid.security import Everyone
        request = self._makeOne()
        self.assertEqual(request.effective_principals, [Everyone])

    def test_with_authentication_policy(self):
        request = self._makeOne()
        _registerAuthenticationPolicy(request.registry, 'yo')
        self.assertEqual(request.effective_principals, 'yo')

    def test_with_authentication_policy_no_reg_on_request(self):
        from pyramid.threadlocal import get_current_registry
        registry = get_current_registry()
        request = self._makeOne()
        del request.registry
        _registerAuthenticationPolicy(registry, 'yo')
        self.assertEqual(request.effective_principals, 'yo')

class ResponseCallbackTestMixin(AuthenticationAPIMixinTest):

    def assert_headers_set(self, request):
        request._process_response_callbacks(request.response)
        headers = request.response.headerlist
        self.assertTrue((_TEST_HEADER, self.principal) in headers, msg=headers)

class TestRememberUserId(ResponseCallbackTestMixin, unittest.TestCase):
    principal = 'the4th'

    def test_backward_compat_delegates_to_mixin(self):
        request = self._makeFakeOne()
        from pyramid.security import remember
        self.assertEqual(remember(request, 'matt'), 'remember_userid')

    def test_with_no_authentication_policy(self):
        request = self._makeOne()
        headers_before = request.response.headers
        request.remember_userid(self.principal)
        self.assertEqual(headers_before, request.response.headers)

    def test_with_authentication_policy(self):
        request = self._makeOne()
        _registerAuthenticationPolicy(request.registry, self.principal)
        request.remember_userid(self.principal)
        self.assert_headers_set(request)

    def test_with_authentication_policy_no_reg_on_request(self):
        from pyramid.threadlocal import get_current_registry
        registry = get_current_registry()
        request = self._makeOne()
        del request.registry
        _registerAuthenticationPolicy(registry, self.principal)
        request.remember_userid(self.principal)
        self.assert_headers_set(request)

class TestForgetUserId(ResponseCallbackTestMixin, unittest.TestCase):
    principal = 'me-not'

    def _makeOne(self):
        request = super(TestForgetUserId, self)._makeOne()
        request.response.headers.add(_TEST_HEADER, self.principal)
        return request

    def test_backward_compat_delegates_to_mixin(self):
        request = self._makeFakeOne()
        from pyramid.security import forget
        self.assertEqual(forget(request), 'forget_userid')

    def test_with_no_authentication_policy(self):
        request = self._makeOne()
        headers_before = request.response.headers
        request.forget_userid()
        self.assertEqual(headers_before, request.response.headers)

    def test_with_authentication_policy(self):
        request = self._makeOne()
        policy = _registerAuthenticationPolicy(request.registry, self.principal)
        policy._header_remembered = (_TEST_HEADER, self.principal)
        request.forget_userid()
        self.assert_headers_set(request)

    def test_with_authentication_policy_no_reg_on_request(self):
        from pyramid.threadlocal import get_current_registry
        registry = get_current_registry()
        request = self._makeOne()
        del request.registry
        policy = _registerAuthenticationPolicy(registry, self.principal)
        policy._header_remembered = (_TEST_HEADER, self.principal)
        request.forget_userid()
        self.assert_headers_set(request)
        
class TestHasPermission(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self):
        from pyramid.security import AuthorizationAPIMixin
        from pyramid.registry import Registry
        mixin = AuthorizationAPIMixin()
        mixin.registry = Registry()
        mixin.context = object()
        return mixin

    def test_delegates_to_mixin(self):
        mixin = self._makeOne()
        from pyramid.security import has_permission
        self.called_has_permission = False

        def mocked_has_permission(*args, **kw):
            self.called_has_permission = True

        mixin.has_permission = mocked_has_permission
        has_permission('view', object(), mixin)
        self.assertTrue(self.called_has_permission)

    def test_no_authentication_policy(self):
        request = self._makeOne()
        result = request.has_permission('view')
        self.assertTrue(result)
        self.assertEqual(result.msg, 'No authentication policy in use.')

    def test_with_no_authorization_policy(self):
        request = self._makeOne()
        _registerAuthenticationPolicy(request.registry, None)
        self.assertRaises(ValueError,
                          request.has_permission, 'view', context=None)

    def test_with_authn_and_authz_policies_registered(self):
        request = self._makeOne()
        _registerAuthenticationPolicy(request.registry, None)
        _registerAuthorizationPolicy(request.registry, 'yo')
        self.assertEqual(request.has_permission('view', context=None), 'yo')

    def test_with_no_reg_on_request(self):
        from pyramid.threadlocal import get_current_registry
        registry = get_current_registry()
        request = self._makeOne()
        del request.registry
        _registerAuthenticationPolicy(registry, None)
        _registerAuthorizationPolicy(registry, 'yo')
        self.assertEqual(request.has_permission('view'), 'yo')

    def test_with_no_context_passed(self):
        request = self._makeOne()
        self.assertTrue(request.has_permission('view'))

    def test_with_no_context_passed_or_on_request(self):
        request = self._makeOne()
        del request.context
        self.assertRaises(AttributeError, request.has_permission, 'view')

class DummyContext:
    def __init__(self, *arg, **kw):
        self.__dict__.update(kw)

class DummyAuthenticationPolicy:
    def __init__(self, result):
        self.result = result

    def effective_principals(self, request):
        return self.result

    def unauthenticated_userid(self, request):
        return self.result

    def authenticated_userid(self, request):
        return self.result

    def remember(self, request, principal, **kw):
        headers = [('X-Pyramid-Test', principal)]
        self._header_remembered = headers[0]
        return headers

    def forget(self, request):
        return [self._header_remembered]

class DummyAuthorizationPolicy:
    def __init__(self, result):
        self.result = result

    def permits(self, context, principals, permission):
        return self.result

    def principals_allowed_by_permission(self, context, permission):
        return self.result

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
