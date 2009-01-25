import unittest

from zope.testing.cleanup import cleanUp

class TestACLAuthorizer(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.security import ACLAuthorizer
        return ACLAuthorizer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_deny_implicit(self):
        context = DummyContext()
        from repoze.bfg.security import Allow
        ace = (Allow, 'somebodyelse', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        principals = ['fred']
        result = authorizer.permits('read', *principals)

    def test_deny_explicit(self):
        context = DummyContext()
        from repoze.bfg.security import Deny
        ace = (Deny, 'somebodyelse', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        principals = ['somebodyelse']
        result = authorizer.permits('read', *principals)

    def test_permits_no_acl_raises(self):
        context = DummyContext()
        authorizer = self._makeOne(context)
        from repoze.bfg.interfaces import NoAuthorizationInformation
        self.assertRaises(NoAuthorizationInformation,
                          authorizer.permits, (), None)

    def test_permits_deny_implicit_empty_acl(self):
        context = DummyContext()
        context.__acl__ = []
        authorizer = self._makeOne(context)
        result = authorizer.permits((), None)
        self.assertEqual(result, False)
        self.assertEqual(result.ace, None)

    def test_permits_deny_no_principals_implicit(self):
        context = DummyContext()
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Everyone
        acl = [(Allow, Everyone, 'view')]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        result = authorizer.permits(None)
        self.assertEqual(result, False)
        self.assertEqual(result.ace, None)

    def test_permits_deny_oneacl_implicit(self):
        context = DummyContext()
        from repoze.bfg.security import Allow
        acl = [(Allow, 'somebody', 'view')]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        result = authorizer.permits('view', 'somebodyelse')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, None)

    def test_permits_deny_twoacl_implicit(self):
        context = DummyContext()
        from repoze.bfg.security import Allow
        acl = [(Allow, 'somebody', 'view'), (Allow, 'somebody', 'write')]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        result = authorizer.permits('view', 'somebodyelse')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, None)

    def test_permits_deny_oneacl_explcit(self):
        context = DummyContext()
        from repoze.bfg.security import Deny
        ace = (Deny, 'somebody', 'view')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        result = authorizer.permits('view', 'somebody')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, ace)

    def test_permits_deny_oneacl_multiperm_explcit(self):
        context = DummyContext()
        acl = []
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Allow
        deny = (Deny, 'somebody', ('view', 'read'))
        allow = (Allow, 'somebody', 'view')
        acl = [deny, allow]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        result = authorizer.permits('view', 'somebody')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, deny)

    def test_permits_deny_twoacl_explicit(self):
        context = DummyContext()
        acl = []
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Allow
        allow = (Allow, 'somebody', 'read')
        deny = (Deny, 'somebody', 'view')
        acl = [allow, deny]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        result = authorizer.permits('view', 'somebody')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, deny)

    def test_permits_allow_twoacl_explicit(self):
        context = DummyContext()
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Allow
        allow = (Allow, 'somebody', 'read')
        deny = (Deny, 'somebody', 'view')
        acl = [allow, deny]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        result = authorizer.permits('read', 'somebody')
        self.assertEqual(result, True)
        self.assertEqual(result.ace, allow)

    def test_permits_nested_principals_list_allow(self):
        context = DummyContext()
        acl = []
        from repoze.bfg.security import Allow
        ace = (Allow, 'larry', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        principals = (['fred', ['jim', ['bob', 'larry']]])
        result = authorizer.permits('read', *principals)
        self.assertEqual(result, True)
        self.assertEqual(result.ace, ace)

    def test_permits_nested_principals_list_deny_explicit(self):
        context = DummyContext()
        from repoze.bfg.security import Deny
        ace = (Deny, 'larry', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        principals = (['fred', ['jim', ['bob', 'larry']]])
        result = authorizer.permits('read', *principals)
        self.assertEqual(result, False)
        self.assertEqual(result.ace, ace)

    def test_permits_nested_principals_list_deny_implicit(self):
        context = DummyContext()
        from repoze.bfg.security import Allow
        ace = (Allow, 'somebodyelse', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context)
        principals = (['fred', ['jim', ['bob', 'larry']]])
        result = authorizer.permits('read', *principals)
        self.assertEqual(result, False)

    def test_permits_allow_via_location_parent(self):
        context = DummyContext()
        context.__parent__ = None
        context.__name__ = None
        from repoze.bfg.security import Allow
        ace = (Allow, 'fred', 'read')
        acl = [ace]
        context.__acl__ = acl
        context2 = DummyContext()
        context2.__parent__ = context
        context2.__name__ = 'myname'
        authorizer = self._makeOne(context)
        principals = ['fred']
        result = authorizer.permits('read', *principals)
        self.assertEqual(result, True)


class TestACLSecurityPolicy(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.security import ACLSecurityPolicy
        return ACLSecurityPolicy

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_class_implements_ISecurityPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ISecurityPolicy
        verifyClass(ISecurityPolicy, self._getTargetClass())

    def test_instance_implements_ISecurityPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ISecurityPolicy
        verifyObject(ISecurityPolicy, self._makeOne(lambda *arg: None))

    def test_permits_no_principals_no_acl_info_on_context(self):
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne(lambda *arg: None)
        authorizer_factory = make_authorizer_factory(None)
        policy.authorizer_factory = authorizer_factory
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        from repoze.bfg.security import Everyone
        self.assertEqual(authorizer_factory.principals, (Everyone,))
        self.assertEqual(authorizer_factory.permission, 'view')
        self.assertEqual(authorizer_factory.context, context)

    def test_permits_no_principals_acl_info_on_context(self):
        context = DummyContext()
        context.__acl__ = []
        request = DummyRequest({})
        policy = self._makeOne(lambda *arg: None)
        authorizer_factory = make_authorizer_factory(None)
        policy.authorizer_factory = authorizer_factory
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        from repoze.bfg.security import Everyone
        self.assertEqual(authorizer_factory.principals, (Everyone,))
        self.assertEqual(authorizer_factory.permission, 'view')
        self.assertEqual(authorizer_factory.context, context)

    def test_permits_default_deny(self):
        context = DummyContext()
        context.__acl__ = []
        request = DummyRequest({})
        policy = self._makeOne(lambda *arg: None)
        authorizer_factory = make_authorizer_factory(None,
                                                     intermediates_raise=True)
        policy.authorizer_factory = authorizer_factory
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        from repoze.bfg.security import Everyone
        self.assertEqual(authorizer_factory.principals, (Everyone,))
        self.assertEqual(authorizer_factory.permission, 'view')
        self.assertEqual(authorizer_factory.context, context)

    def test_permits_no_principals_withparents_root_has_acl_info(self):
        context = DummyContext()
        context.__name__ = None
        context.__parent__ = None
        context2 = DummyContext()
        context2.__name__ = 'context2'
        context2.__parent__ = context
        context.__acl__ = []
        request = DummyRequest({})
        policy = self._makeOne(lambda *arg: None)
        authorizer_factory = make_authorizer_factory(None)
        policy.authorizer_factory = authorizer_factory
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        from repoze.bfg.security import Everyone
        self.assertEqual(authorizer_factory.principals, (Everyone,))
        self.assertEqual(authorizer_factory.permission, 'view')
        self.assertEqual(authorizer_factory.context, context)

    def test_permits_no_principals_withparents_root_allows_everyone(self):
        context = DummyContext()
        context.__name__ = None
        context.__parent__ = None
        context2 = DummyContext()
        context2.__name__ = 'context2'
        context2.__parent__ = context
        request = DummyRequest({})
        policy = self._makeOne(lambda *arg: None)
        authorizer_factory = make_authorizer_factory(context)
        policy.authorizer_factory = authorizer_factory
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, True)
        from repoze.bfg.security import Everyone
        self.assertEqual(authorizer_factory.principals, (Everyone,))
        self.assertEqual(authorizer_factory.permission, 'view')
        self.assertEqual(authorizer_factory.context, context)

    def test_principals_allowed_by_permission_direct(self):
        from repoze.bfg.security import Allow
        context = DummyContext()
        acl = [ (Allow, 'chrism', ('read', 'write')),
                (Allow, 'other', ('read',)) ]
        context.__acl__ = acl
        policy = self._makeOne(lambda *arg: None)
        result = policy.principals_allowed_by_permission(context, 'read')
        self.assertEqual(result, ['chrism', 'other'])

    def test_principals_allowed_by_permission_acquired(self):
        from repoze.bfg.security import Allow
        context = DummyContext()
        acl = [ (Allow, 'chrism', ('read', 'write')),
                (Allow, 'other', ('read',)) ]
        context.__acl__ = acl
        context.__parent__ = None
        context.__name__ = 'context'
        inter = DummyContext()
        inter.__name__ = None
        inter.__parent__ = context
        policy = self._makeOne(lambda *arg: None)
        result = policy.principals_allowed_by_permission(inter, 'read')
        self.assertEqual(result, ['chrism', 'other'])

    def test_principals_allowed_by_permission_no_acls(self):
        policy = self._makeOne(lambda *arg: None)
        result = policy.principals_allowed_by_permission(None, 'read')
        self.assertEqual(result, [])

class TestRemoteUserACLSecurityPolicy(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.security import RemoteUserACLSecurityPolicy
        return RemoteUserACLSecurityPolicy

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ISecurityPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ISecurityPolicy
        verifyObject(ISecurityPolicy, self._makeOne())

    def test_authenticated_userid(self):
        context = DummyContext()
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        result = policy.authenticated_userid(request)
        self.assertEqual(result, 'fred')

    def test_authenticated_userid_no_remote_user(self):
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.authenticated_userid(request)
        self.assertEqual(result, None)

    def test_effective_principals(self):
        context = DummyContext()
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        result = policy.effective_principals(request)
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        self.assertEqual(result, [Everyone, Authenticated, 'fred'])

    def test_effective_principals_no_remote_user(self):
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.effective_principals(request)
        from repoze.bfg.security import Everyone
        self.assertEqual(result, [Everyone])

class TestRepozeWhoIdentityACLSecurityPolicy(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.security import RepozeWhoIdentityACLSecurityPolicy
        return RepozeWhoIdentityACLSecurityPolicy

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ISecurityPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ISecurityPolicy
        verifyObject(ISecurityPolicy, self._makeOne())

    def test_authenticated_userid(self):
        context = DummyContext()
        identity = {'repoze.who.identity':{'repoze.who.userid':'fred'}}
        request = DummyRequest(identity)
        policy = self._makeOne()
        result = policy.authenticated_userid(request)
        self.assertEqual(result, 'fred')

    def test_authenticated_userid_no_who_ident(self):
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.authenticated_userid(request)
        self.assertEqual(result, None)

    def test_effective_principals(self):
        context = DummyContext()
        identity = {'repoze.who.identity':{'repoze.who.userid':'fred'}}
        request = DummyRequest(identity)
        policy = self._makeOne()
        result = policy.effective_principals(request)
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        self.assertEqual(result, [Everyone, Authenticated, 'fred'])

    def test_effective_principals_no_who_ident(self):
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.effective_principals(request)
        from repoze.bfg.security import Everyone
        self.assertEqual(result, [Everyone])

class TestAPIFunctions(unittest.TestCase):
    def setUp(self):
        cleanUp()
        
    def tearDown(self):
        cleanUp()

    def _registerSecurityPolicy(self, secpol):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import ISecurityPolicy
        gsm.registerUtility(secpol, ISecurityPolicy)

    def test_has_permission_registered(self):
        secpol = DummySecurityPolicy(False)
        self._registerSecurityPolicy(secpol)
        from repoze.bfg.security import has_permission
        self.assertEqual(has_permission('view', None, None), False)
        
    def test_has_permission_not_registered(self):
        from repoze.bfg.security import has_permission
        result = has_permission('view', None, None)
        self.assertEqual(result, True)
        self.assertEqual(result.msg, 'No security policy in use.')

    def test_authenticated_userid_registered(self):
        secpol = DummySecurityPolicy(False)
        self._registerSecurityPolicy(secpol)
        from repoze.bfg.security import authenticated_userid
        request = DummyRequest({})
        self.assertEqual(authenticated_userid(request), 'fred')
        
    def test_authenticated_userid_not_registered(self):
        from repoze.bfg.security import authenticated_userid
        request = DummyRequest({})
        self.assertEqual(authenticated_userid(request), None)

    def test_effective_principals_registered(self):
        secpol = DummySecurityPolicy(False)
        self._registerSecurityPolicy(secpol)
        from repoze.bfg.security import effective_principals
        request = DummyRequest({})
        self.assertEqual(effective_principals(request), ['fred', 'bob'])
        
    def test_effective_principals_not_registered(self):
        from repoze.bfg.security import effective_principals
        request = DummyRequest({})
        self.assertEqual(effective_principals(request), [])

    def test_principals_allowed_by_permission_not_registered(self):
        from repoze.bfg.security import principals_allowed_by_permission
        from repoze.bfg.security import Everyone
        self.assertEqual(principals_allowed_by_permission(None, None),
                         [Everyone])

    def test_principals_allowed_by_permission_registered(self):
        secpol = DummySecurityPolicy(False)
        self._registerSecurityPolicy(secpol)
        from repoze.bfg.security import principals_allowed_by_permission
        self.assertEqual(principals_allowed_by_permission(None, None),
                         ['fred', 'bob'])

class TestViewPermission(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.security import ViewPermission
        return ViewPermission
    
    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)
        
    def test_call(self):
        context = DummyContext()
        request = DummyRequest({})
        secpol = DummySecurityPolicy(True)
        permission = self._makeOne(context, request, 'repoze.view')
        result = permission(secpol)
        self.assertEqual(result, True)
        self.assertEqual(secpol.checked, (context, request, 'repoze.view'))

    def test_repr(self):
        context = DummyContext()
        request = DummyRequest({})
        request.view_name = 'viewname'
        secpol = DummySecurityPolicy(True)
        permission = self._makeOne(context, request, 'repoze.view')
        result = repr(permission)
        self.failUnless(result.startswith('<Permission at '))
        self.failUnless(result.endswith(" named 'repoze.view' for 'viewname'>"))

class TestViewPermissionFactory(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.security import ViewPermissionFactory
        return ViewPermissionFactory
    
    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)
        
    def test_call(self):
        context = DummyContext()
        request = DummyRequest({})
        factory = self._makeOne('repoze.view')
        result = factory(context, request)
        self.assertEqual(result.permission_name, 'repoze.view')
        self.assertEqual(result.context, context)
        self.assertEqual(result.request, request)

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

class TestFlatten(unittest.TestCase):
    def _callFUT(self, item):
        from repoze.bfg.security import flatten
        return flatten(item)

    def test_str(self):
        result = self._callFUT('a')
        self.assertEqual(result, ['a'])

    def test_unicode(self):
        result = self._callFUT(u'a')
        self.assertEqual(result, [u'a'])

    def test_flat_sequence(self):
        result = self._callFUT([1, 2, 3])
        self.assertEqual(result, [1, 2, 3])

    def test_singly_nested_sequence(self):
        result = self._callFUT([1, [2, 3]])
        self.assertEqual(result, [1, 2, 3])
        
    def test_doubly_nested_sequence(self):
        result = self._callFUT([1, [2, [3]]])
        self.assertEqual(result, [1, 2, 3])

    def test_mix_str_unicode_sequence(self):
        result = self._callFUT([1, [2, [3]], u'a', ('b', set(['c', 'd']))])
        self.assertEqual(result, [1, 2, 3, u'a', 'b', 'c', 'd'])

class DummyContext:
    pass

class DummyRequest:
    def __init__(self, environ):
        self.environ = environ

class DummySecurityPolicy:
    def __init__(self, result):
        self.result = result

    def permits(self, *args):
        self.checked = args
        return self.result

    def authenticated_userid(self, request):
        return 'fred'

    def effective_principals(self, request):
        return ['fred', 'bob']

    def principals_allowed_by_permission(self, context, permission):
        return ['fred', 'bob']

class make_authorizer_factory:
    def __init__(self, expected_context, intermediates_raise=False):
        self.expected_context = expected_context
        self.intermediates_raise = intermediates_raise

    def __call__(self, context):
        authorizer = self
        class Authorizer:
            def permits(self, permission, *principals):
                authorizer.permission = permission
                authorizer.principals = principals
                authorizer.context = context
                result = authorizer.expected_context == context
                if not result and authorizer.intermediates_raise:
                    from repoze.bfg.interfaces import NoAuthorizationInformation
                    raise NoAuthorizationInformation()
                return result
        return Authorizer()
