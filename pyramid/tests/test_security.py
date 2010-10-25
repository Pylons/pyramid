import unittest

from repoze.bfg.testing import cleanUp


class TestAllPermissionsList(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.security import AllPermissionsList
        return AllPermissionsList

    def _makeOne(self):
        return self._getTargetClass()()

    def test_it(self):
        thing = self._makeOne()
        self.failUnless(thing.__eq__(thing))
        self.assertEqual(thing.__iter__(), ())
        self.failUnless('anything' in thing)

    def test_singleton(self):
        from repoze.bfg.security import ALL_PERMISSIONS
        self.assertEqual(ALL_PERMISSIONS.__class__, self._getTargetClass())

class TestAllowed(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.security import Allowed
        return Allowed
    
    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_it(self):
        allowed = self._makeOne('hello')
        self.assertEqual(allowed.msg, 'hello')
        self.assertEqual(allowed, True)
        self.failUnless(allowed)
        self.assertEqual(str(allowed), 'hello')
        self.failUnless('<Allowed instance at ' in repr(allowed))
        self.failUnless("with msg 'hello'>" in repr(allowed))

class TestDenied(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.security import Denied
        return Denied
    
    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_it(self):
        denied = self._makeOne('hello')
        self.assertEqual(denied.msg, 'hello')
        self.assertEqual(denied, False)
        self.failIf(denied)
        self.assertEqual(str(denied), 'hello')
        self.failUnless('<Denied instance at ' in repr(denied))
        self.failUnless("with msg 'hello'>" in repr(denied))

class TestACLAllowed(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.security import ACLAllowed
        return ACLAllowed
    
    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_it(self):
        msg = ("ACLAllowed permission 'permission' via ACE 'ace' in ACL 'acl' "
               "on context 'ctx' for principals 'principals'")
        allowed = self._makeOne('ace', 'acl', 'permission', 'principals', 'ctx')
        self.failUnless(msg in allowed.msg)
        self.assertEqual(allowed, True)
        self.failUnless(allowed)
        self.assertEqual(str(allowed), msg)
        self.failUnless('<ACLAllowed instance at ' in repr(allowed))
        self.failUnless("with msg %r>" % msg in repr(allowed))

class TestACLDenied(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.security import ACLDenied
        return ACLDenied
    
    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_it(self):
        msg = ("ACLDenied permission 'permission' via ACE 'ace' in ACL 'acl' "
               "on context 'ctx' for principals 'principals'")
        denied = self._makeOne('ace', 'acl', 'permission', 'principals', 'ctx')
        self.failUnless(msg in denied.msg)
        self.assertEqual(denied, False)
        self.failIf(denied)
        self.assertEqual(str(denied), msg)
        self.failUnless('<ACLDenied instance at ' in repr(denied))
        self.failUnless("with msg %r>" % msg in repr(denied))

class TestViewExecutionPermitted(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.security import view_execution_permitted
        return view_execution_permitted(*arg, **kw)

    def _registerSecuredView(self, view_name, allow=True):
        from repoze.bfg.threadlocal import get_current_registry
        from zope.interface import Interface
        from repoze.bfg.interfaces import ISecuredView
        from repoze.bfg.interfaces import IViewClassifier
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
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import ISettings
        settings = dict(debug_authorization=True)
        reg = get_current_registry()
        reg.registerUtility(settings, ISettings)
        context = DummyContext()
        request = DummyRequest({})
        result = self._callFUT(context, request, '')
        msg = result.msg
        self.failUnless("Allowed: view name '' in context" in msg)
        self.failUnless('(no permission defined)' in msg)
        self.assertEqual(result, True)

    def test_with_permission(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerSecuredView('', True)
        request = DummyRequest({})
        directlyProvides(request, IRequest)
        result = self._callFUT(context, request, '')
        self.failUnless(result is True)

class TestHasPermission(unittest.TestCase):
    def setUp(self):
        cleanUp()
        
    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg):
        from repoze.bfg.security import has_permission
        return has_permission(*arg)

    def test_no_authentication_policy(self):
        request = _makeRequest()
        result = self._callFUT('view', None, request)
        self.assertEqual(result, True)
        self.assertEqual(result.msg, 'No authentication policy in use.')
        
    def test_authentication_policy_no_authorization_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, None)
        self.assertRaises(ValueError, self._callFUT, 'view', None, request)

    def test_authn_and_authz_policies_registered(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, None)
        _registerAuthorizationPolicy(request.registry, 'yo')
        self.assertEqual(self._callFUT('view', None, request), 'yo')

    def test_no_registry_on_request(self):
        from repoze.bfg.threadlocal import get_current_registry
        request = DummyRequest({})
        registry = get_current_registry()
        _registerAuthenticationPolicy(registry, None)
        _registerAuthorizationPolicy(registry, 'yo')
        self.assertEqual(self._callFUT('view', None, request), 'yo')

class TestAuthenticatedUserId(unittest.TestCase):
    def setUp(self):
        cleanUp()
        
    def tearDown(self):
        cleanUp()

    def _callFUT(self, request):
        from repoze.bfg.security import authenticated_userid
        return authenticated_userid(request)

    def test_no_authentication_policy(self):
        request = _makeRequest()
        result = self._callFUT(request)
        self.assertEqual(result, None)

    def test_with_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        result = self._callFUT(request)
        self.assertEqual(result, 'yo')

    def test_with_authentication_policy_no_reg_on_request(self):
        from repoze.bfg.threadlocal import get_current_registry
        request = DummyRequest({})
        registry = get_current_registry()
        _registerAuthenticationPolicy(registry, 'yo')
        result = self._callFUT(request)
        self.assertEqual(result, 'yo')

class TestEffectivePrincipals(unittest.TestCase):
    def setUp(self):
        cleanUp()
        
    def tearDown(self):
        cleanUp()

    def _callFUT(self, request):
        from repoze.bfg.security import effective_principals
        return effective_principals(request)

    def test_no_authentication_policy(self):
        request = _makeRequest()
        result = self._callFUT(request)
        self.assertEqual(result, [])

    def test_with_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        result = self._callFUT(request)
        self.assertEqual(result, 'yo')

    def test_with_authentication_policy_no_reg_on_request(self):
        from repoze.bfg.threadlocal import get_current_registry
        registry = get_current_registry()
        request = DummyRequest({})
        _registerAuthenticationPolicy(registry, 'yo')
        result = self._callFUT(request)
        self.assertEqual(result, 'yo')

class TestPrincipalsAllowedByPermission(unittest.TestCase):
    def setUp(self):
        cleanUp()
        
    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg):
        from repoze.bfg.security import principals_allowed_by_permission
        return principals_allowed_by_permission(*arg)

    def test_no_authorization_policy(self):
        from repoze.bfg.security import Everyone
        context = DummyContext()
        result = self._callFUT(context, 'view')
        self.assertEqual(result, [Everyone])

    def test_with_authorization_policy(self):
        from repoze.bfg.threadlocal import get_current_registry
        registry = get_current_registry()
        _registerAuthorizationPolicy(registry, 'yo')
        context = DummyContext()
        result = self._callFUT(context, 'view')
        self.assertEqual(result, 'yo')

class TestRemember(unittest.TestCase):
    def setUp(self):
        cleanUp()
        
    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg):
        from repoze.bfg.security import remember
        return remember(*arg)

    def test_no_authentication_policy(self):
        request = _makeRequest()
        result = self._callFUT(request, 'me')
        self.assertEqual(result, [])

    def test_with_authentication_policy(self):
        request = _makeRequest()
        registry = request.registry
        _registerAuthenticationPolicy(registry, 'yo')
        result = self._callFUT(request, 'me')
        self.assertEqual(result, 'yo')

    def test_with_authentication_policy_no_reg_on_request(self):
        from repoze.bfg.threadlocal import get_current_registry
        registry = get_current_registry()
        request = DummyRequest({})
        _registerAuthenticationPolicy(registry, 'yo')
        result = self._callFUT(request, 'me')
        self.assertEqual(result, 'yo')

class TestForget(unittest.TestCase):
    def setUp(self):
        cleanUp()
        
    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg):
        from repoze.bfg.security import forget
        return forget(*arg)

    def test_no_authentication_policy(self):
        request = _makeRequest()
        result = self._callFUT(request)
        self.assertEqual(result, [])

    def test_with_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        result = self._callFUT(request)
        self.assertEqual(result, 'yo')

    def test_with_authentication_policy_no_reg_on_request(self):
        from repoze.bfg.threadlocal import get_current_registry
        registry = get_current_registry()
        request = DummyRequest({})
        _registerAuthenticationPolicy(registry, 'yo')
        result = self._callFUT(request)
        self.assertEqual(result, 'yo')

class DummyContext:
    def __init__(self, *arg, **kw):
        self.__dict__.update(kw)

class DummyRequest:
    def __init__(self, environ):
        self.environ = environ

class DummyAuthenticationPolicy:
    def __init__(self, result):
        self.result = result

    def effective_principals(self, request):
        return self.result

    def authenticated_userid(self, request):
        return self.result

    def remember(self, request, principal, **kw):
        return self.result

    def forget(self, request):
        return self.result

class DummyAuthorizationPolicy:
    def __init__(self, result):
        self.result = result

    def permits(self, context, principals, permission):
        return self.result

    def principals_allowed_by_permission(self, context, permission):
        return self.result

def _registerAuthenticationPolicy(reg, result):
    from repoze.bfg.interfaces import IAuthenticationPolicy
    policy = DummyAuthenticationPolicy(result)
    reg.registerUtility(policy, IAuthenticationPolicy)
    return policy

def _registerAuthorizationPolicy(reg, result):
    from repoze.bfg.interfaces import IAuthorizationPolicy
    policy = DummyAuthorizationPolicy(result)
    reg.registerUtility(policy, IAuthorizationPolicy)
    return policy

def _makeRequest():
    from repoze.bfg.registry import Registry
    request = DummyRequest({})
    request.registry = Registry()
    return request


