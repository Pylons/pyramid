import unittest

from repoze.bfg.testing import cleanUp

class TestAPIFunctionsSecpolBBB(unittest.TestCase):
    def setUp(self):
        cleanUp()
        
    def tearDown(self):
        cleanUp()
        try:
            del globals()['__warningregistry__']
        except KeyError:
            pass

    def _testWithWarnings(self, f, *args, **kw):
        messages = []
        def showwarning(message, category, filename, lineno, file=None):
            messages.append(message)
        try:
            import warnings
            _old_showwarning = warnings.showwarning
            warnings.showwarning = showwarning
            result = f(*args, **kw)
            return result, messages
        finally:
            warnings.showwarning = _old_showwarning

    def _registerSecurityPolicy(self, secpol):
        import zope.component
        from repoze.bfg.secpols import registerBBBAuthn
        gsm = zope.component.getGlobalSiteManager()
        registerBBBAuthn(secpol, gsm)

    def test_has_permission_registered(self):
        secpol = DummySecurityPolicy(False)
        self._registerSecurityPolicy(secpol)
        from repoze.bfg.security import has_permission
        self.assertEqual(has_permission('view', None, None), False)
        
    def test_has_permission_not_registered(self):
        from repoze.bfg.security import has_permission
        result = has_permission('view', None, None)
        self.assertEqual(result, True)
        self.assertEqual(result.msg, 'No authentication policy in use.')

    def test_authenticated_userid_registered(self):
        secpol = DummySecurityPolicy(False)
        self._registerSecurityPolicy(secpol)
        from repoze.bfg.security import authenticated_userid
        request = DummyRequest({})
        result, warnings = self._testWithWarnings(authenticated_userid,
                                                  request)
        self.assertEqual(result, 'fred')
        self.assertEqual(len(warnings), 1)
        
    def test_authenticated_userid_not_registered(self):
        from repoze.bfg.security import authenticated_userid
        request = DummyRequest({})
        result, warnings = self._testWithWarnings(authenticated_userid,
                                                  request)
        self.assertEqual(result, None)
        self.assertEqual(len(warnings), 1)

    def test_authenticated_userid_too_many_args(self):
        from repoze.bfg.security import authenticated_userid
        self.assertRaises(TypeError, authenticated_userid, None, None, None)

    def test_effective_principals_registered(self):
        secpol = DummySecurityPolicy(False)
        self._registerSecurityPolicy(secpol)
        from repoze.bfg.security import effective_principals
        request = DummyRequest({})
        result, warnings = self._testWithWarnings(effective_principals, request)
        self.assertEqual(result, ['fred', 'bob'])
        self.assertEqual(len(warnings), 1)
        
    def test_effective_principals_not_registered(self):
        from repoze.bfg.security import effective_principals
        request = DummyRequest({})
        result, warnings = self._testWithWarnings(effective_principals, request)
        self.assertEqual(result, [])
        self.assertEqual(len(warnings), 1)

    def test_effective_principals_too_many_args(self):
        from repoze.bfg.security import effective_principals
        self.assertRaises(TypeError, effective_principals, None, None, None)


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


class TestACLSecurityPolicy(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.secpols import ACLSecurityPolicy
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
        policy = self._makeOne(lambda *arg: [])
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        from repoze.bfg.security import Everyone
        self.assertEqual(result.principals, set([Everyone]))
        self.assertEqual(result.permission, 'view')
        self.assertEqual(result.context, context)

    def test_permits_no_principals_empty_acl_info_on_context(self):
        context = DummyContext()
        context.__acl__ = []
        request = DummyRequest({})
        policy = self._makeOne(lambda *arg: [])
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        from repoze.bfg.security import Everyone
        self.assertEqual(result.principals, set([Everyone]))
        self.assertEqual(result.permission, 'view')
        self.assertEqual(result.context, context)

    def test_permits_no_principals_root_has_empty_acl_info(self):
        context = DummyContext()
        context.__name__ = None
        context.__parent__ = None
        context.__acl__ = []
        context2 = DummyContext()
        context2.__name__ = 'context2'
        context2.__parent__ = context
        request = DummyRequest({})
        policy = self._makeOne(lambda *arg: [])
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        from repoze.bfg.security import Everyone
        self.assertEqual(result.principals, set([Everyone]))
        self.assertEqual(result.permission, 'view')
        self.assertEqual(result.context, context)

    def test_permits_no_principals_root_allows_everyone(self):
        context = DummyContext()
        context.__name__ = None
        context.__parent__ = None
        from repoze.bfg.security import Allow, Everyone
        context.__acl__ = [ (Allow, Everyone, 'view') ]
        context2 = DummyContext()
        context2.__name__ = 'context2'
        context2.__parent__ = context
        request = DummyRequest({})
        policy = self._makeOne(lambda *arg: [])
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.principals, set([Everyone]))
        self.assertEqual(result.permission, 'view')
        self.assertEqual(result.context, context)

    def test_permits_deny_implicit(self):
        from repoze.bfg.security import Allow, Authenticated, Everyone
        context = DummyContext()
        context.__acl__ =  [ (Allow, 'somebodyelse', 'read') ]
        policy = self._makeOne(lambda *arg: ['fred'])
        request = DummyRequest({})
        result = policy.permits(context, request, 'read')
        self.assertEqual(result, False)
        self.assertEqual(result.principals,
                         set(['fred', Authenticated, Everyone]))
        self.assertEqual(result.permission, 'read')
        self.assertEqual(result.context, context)
        self.assertEqual(result.ace, None)

    def test_permits_deny_explicit(self):
        from repoze.bfg.security import Deny, Authenticated, Everyone
        context = DummyContext()
        context.__acl__ =  [ (Deny, 'fred', 'read') ]
        policy = self._makeOne(lambda *arg: ['fred'])
        request = DummyRequest({})
        result = policy.permits(context, request, 'read')
        self.assertEqual(result, False)
        self.assertEqual(result.principals,
                         set(['fred', Authenticated, Everyone]))
        self.assertEqual(result.permission, 'read')
        self.assertEqual(result.context, context)
        self.assertEqual(result.ace, (Deny, 'fred', 'read'))

    def test_permits_deny_twoacl_implicit(self):
        from repoze.bfg.security import Allow, Authenticated, Everyone
        context = DummyContext()
        acl = [(Allow, 'somebody', 'view'), (Allow, 'somebody', 'write')]
        context.__acl__ = acl
        policy = self._makeOne(lambda *arg: ['fred'])
        request = DummyRequest({})
        result = policy.permits(context, request, 'read')
        self.assertEqual(result, False)
        self.assertEqual(result.principals,
                         set(['fred', Authenticated, Everyone]))
        self.assertEqual(result.permission, 'read')
        self.assertEqual(result.context, context)
        self.assertEqual(result.ace, None)

    def test_permits_allow_twoacl_multiperm(self):
        from repoze.bfg.security import Allow, Deny, Authenticated, Everyone
        context = DummyContext()
        acl = [ (Allow, 'fred', ('write', 'view') ), (Deny, 'fred', 'view') ]
        context.__acl__ = acl
        policy = self._makeOne(lambda *arg: ['fred'])
        request = DummyRequest({})
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.principals,
                         set(['fred', Authenticated, Everyone]))
        self.assertEqual(result.permission, 'view')
        self.assertEqual(result.context, context)
        self.assertEqual(result.ace, (Allow, 'fred', ('write', 'view') ))

    def test_permits_deny_twoacl_multiperm(self):
        from repoze.bfg.security import Allow, Deny, Authenticated, Everyone
        context = DummyContext()
        acl = []
        deny = (Deny, 'fred', ('view', 'read'))
        allow = (Allow, 'fred', 'view')
        context.__acl__ = [deny, allow]
        policy = self._makeOne(lambda *arg: ['fred'])
        request = DummyRequest({})
        result = policy.permits(context, request, 'read')
        self.assertEqual(result, False)
        self.assertEqual(result.principals,
                         set(['fred', Authenticated, Everyone]))
        self.assertEqual(result.permission, 'read')
        self.assertEqual(result.context, context)
        self.assertEqual(result.ace, deny)

    def test_permits_allow_via_location_parent(self):
        from repoze.bfg.security import Allow, Authenticated, Everyone
        context = DummyContext()
        context.__parent__ = None
        context.__name__ = None
        context.__acl__ = [ (Allow, 'fred', 'read') ]
        context2 = DummyContext()
        context2.__parent__ = context
        context2.__name__ = 'myname'

        policy = self._makeOne(lambda *arg: ['fred'])
        request = DummyRequest({})
        result = policy.permits(context2, request, 'read')
        self.assertEqual(result, True)
        self.assertEqual(result.principals,
                         set(['fred', Authenticated, Everyone]))
        self.assertEqual(result.permission, 'read')
        self.assertEqual(result.context, context)
        self.assertEqual(result.ace, ('Allow', 'fred', 'read'))

    def test_permits_deny_byorder(self):
        from repoze.bfg.security import Allow, Deny, Authenticated, Everyone
        context = DummyContext()
        acl = []
        deny = (Deny, 'fred', 'read')
        allow = (Allow, 'fred', 'view')
        context.__acl__ = [deny, allow]
        policy = self._makeOne(lambda *arg: ['fred'])
        request = DummyRequest({})
        result = policy.permits(context, request, 'read')
        self.assertEqual(result, False)
        self.assertEqual(result.principals,
                         set(['fred', Authenticated, Everyone]))
        self.assertEqual(result.permission, 'read')
        self.assertEqual(result.context, context)
        self.assertEqual(result.ace, deny)

    def test_permits_allow_byorder(self):
        from repoze.bfg.security import Allow, Deny, Authenticated, Everyone
        context = DummyContext()
        acl = []
        deny = (Deny, 'fred', ('view', 'read'))
        allow = (Allow, 'fred', 'view')
        context.__acl__ = [allow, deny]
        policy = self._makeOne(lambda *arg: ['fred'])
        request = DummyRequest({})
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.principals,
                         set(['fred', Authenticated, Everyone]))
        self.assertEqual(result.permission, 'view')
        self.assertEqual(result.context, context)
        self.assertEqual(result.ace, allow)

    def test_principals_allowed_by_permission_direct(self):
        from repoze.bfg.security import Allow
        context = DummyContext()
        acl = [ (Allow, 'chrism', ('read', 'write')),
                (Allow, 'other', 'read') ]
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

class TestInheritingACLSecurityPolicy(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.secpols import InheritingACLSecurityPolicy
        return InheritingACLSecurityPolicy

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

    def test_permits(self):
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        from repoze.bfg.security import ALL_PERMISSIONS
        from repoze.bfg.security import DENY_ALL
        policy = self._makeOne(lambda *arg: [])
        root = DummyContext()
        community = DummyContext(__name__='community', __parent__=root)
        blog = DummyContext(__name__='blog', __parent__=community)
        root.__acl__ = [
            (Allow, Authenticated, VIEW),
            ]
        community.__acl__ = [
            (Allow, 'fred', ALL_PERMISSIONS),
            (Allow, 'wilma', VIEW),
            DENY_ALL,
            ]
        blog.__acl__ = [
            (Allow, 'barney', MEMBER_PERMS),
            (Allow, 'wilma', VIEW),
            ]
        policy = self._makeOne(lambda request: request.principals)
        request = DummyRequest({})

        request.principals = ['wilma']
        result = policy.permits(blog, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, blog)
        self.assertEqual(result.ace, (Allow, 'wilma', VIEW))
        result = policy.permits(blog, request, 'delete')
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))

        request.principals = ['fred']
        result = policy.permits(blog, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'fred', ALL_PERMISSIONS))
        result = policy.permits(blog, request, 'doesntevenexistyet')
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'fred', ALL_PERMISSIONS))

        request.principals = ['barney']
        result = policy.permits(blog, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, blog)
        self.assertEqual(result.ace, (Allow, 'barney', MEMBER_PERMS))
        result = policy.permits(blog, request, 'administer')
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))
        
        request.principals = ['someguy']
        result = policy.permits(root, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, root)
        self.assertEqual(result.ace, (Allow, Authenticated, VIEW))
        result = policy.permits(blog, request, 'view')
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))

        request.principals = []
        result = policy.permits(root, request, 'view')
        self.assertEqual(result, False)
        self.assertEqual(result.context, root)
        self.assertEqual(result.ace, None)

        request.principals = []
        context = DummyContext()
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)

    def test_principals_allowed_by_permission_direct(self):
        from repoze.bfg.security import Allow
        from repoze.bfg.security import DENY_ALL
        context = DummyContext()
        acl = [ (Allow, 'chrism', ('read', 'write')),
                DENY_ALL,
                (Allow, 'other', 'read') ]
        context.__acl__ = acl
        policy = self._makeOne(lambda *arg: None)
        result = sorted(
            policy.principals_allowed_by_permission(context, 'read'))
        self.assertEqual(result, ['chrism'])

    def test_principals_allowed_by_permission(self):
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Deny
        from repoze.bfg.security import DENY_ALL
        from repoze.bfg.security import ALL_PERMISSIONS
        root = DummyContext(__name__='', __parent__=None)
        community = DummyContext(__name__='community', __parent__=root)
        blog = DummyContext(__name__='blog', __parent__=community)
        root.__acl__ = [ (Allow, 'chrism', ('read', 'write')),
                         (Allow, 'other', ('read',)),
                         (Allow, 'jim', ALL_PERMISSIONS)]
        community.__acl__ = [  (Deny, 'flooz', 'read'),
                               (Allow, 'flooz', 'read'),
                               (Allow, 'mork', 'read'),
                               (Deny, 'jim', 'read'),
                               (Allow, 'someguy', 'manage')]
        blog.__acl__ = [ (Allow, 'fred', 'read'),
                         DENY_ALL]
        
        policy = self._makeOne(lambda *arg: None)
        result = sorted(policy.principals_allowed_by_permission(blog, 'read'))
        self.assertEqual(result, ['fred'])
        result = sorted(policy.principals_allowed_by_permission(community,
                                                                'read'))
        self.assertEqual(result, ['chrism', 'mork', 'other'])
        result = sorted(policy.principals_allowed_by_permission(community,
                                                                'read'))
        result = sorted(policy.principals_allowed_by_permission(root, 'read'))
        self.assertEqual(result, ['chrism', 'jim', 'other'])

    def test_principals_allowed_by_permission_no_acls(self):
        policy = self._makeOne(lambda *arg: None)
        context = DummyContext()
        result = sorted(policy.principals_allowed_by_permission(context,'read'))
        self.assertEqual(result, [])

    def test_effective_principals(self):
        context = DummyContext()
        request = DummyRequest({})
        request.principals = ['fred']
        policy = self._makeOne(lambda request: request.principals)
        result = sorted(policy.effective_principals(request))
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        self.assertEqual(result,
                         ['fred', Authenticated, Everyone])

    def test_no_effective_principals(self):
        context = DummyContext()
        request = DummyRequest({})
        request.principals = []
        policy = self._makeOne(lambda request: request.principals)
        result = sorted(policy.effective_principals(request))
        from repoze.bfg.security import Everyone
        self.assertEqual(result, [Everyone])

    def test_authenticated_userid(self):
        context = DummyContext()
        request = DummyRequest({})
        request.principals = ['fred']
        policy = self._makeOne(lambda request: request.principals)
        result = policy.authenticated_userid(request)
        self.assertEqual(result, 'fred')

    def test_no_authenticated_userid(self):
        context = DummyContext()
        request = DummyRequest({})
        request.principals = []
        policy = self._makeOne(lambda request: request.principals)
        result = policy.authenticated_userid(request)
        self.assertEqual(result, None)

class TestRemoteUserACLSecurityPolicy(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.secpols import RemoteUserACLSecurityPolicy
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

class TestRemoteUserInheritingACLSecurityPolicy(TestRemoteUserACLSecurityPolicy):
    def _getTargetClass(self):
        from repoze.bfg.secpols import RemoteUserInheritingACLSecurityPolicy
        return RemoteUserInheritingACLSecurityPolicy

class TestWhoACLSecurityPolicy(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.secpols import WhoACLSecurityPolicy
        return WhoACLSecurityPolicy

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

class TestWhoInheritingACLSecurityPolicy(TestWhoACLSecurityPolicy):
    def _getTargetClass(self):
        from repoze.bfg.secpols import WhoInheritingACLSecurityPolicy
        return WhoInheritingACLSecurityPolicy

class TestSecurityPolicyToAuthenticationPolicyAdapter(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.secpols import \
             SecurityPolicyToAuthenticationPolicyAdapter
        return SecurityPolicyToAuthenticationPolicyAdapter

    def _makeOne(self, secpol):
        return self._getTargetClass()(secpol)

    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne(None))

    def test_authenticated_userid(self):
        secpol = DummySecurityPolicy(None)
        adapter = self._makeOne(secpol)
        result = adapter.authenticated_userid(None, None)
        self.assertEqual(result, 'fred')
        
    def test_effective_principals(self):
        secpol = DummySecurityPolicy(None)
        adapter = self._makeOne(secpol)
        result = adapter.effective_principals(None, None)
        self.assertEqual(result, ['fred', 'bob'])

    def test_remember(self):
        secpol = DummySecurityPolicy(None)
        adapter = self._makeOne(secpol)
        result = adapter.remember(None, None, None)
        self.assertEqual(result, [])

    def test_forget(self):
        secpol = DummySecurityPolicy(None)
        adapter = self._makeOne(secpol)
        result = adapter.forget(None, None)
        self.assertEqual(result, [])

class TestSecurityPolicyToAuthorizationPolicyAdapter(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.secpols import \
             SecurityPolicyToAuthorizationPolicyAdapter
        return SecurityPolicyToAuthorizationPolicyAdapter

    def _makeOne(self, secpol):
        return self._getTargetClass()(secpol)

    def test_class_implements_IAuthorizationPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IAuthorizationPolicy
        verifyClass(IAuthorizationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthorizationPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IAuthorizationPolicy
        verifyObject(IAuthorizationPolicy, self._makeOne(None))

    def test_permits(self):
        from repoze.bfg.threadlocal import manager
        manager.push({'request':1})
        try:
            secpol = DummySecurityPolicy(None)
            adapter = self._makeOne(secpol)
            result = adapter.permits(None, None, None)
            self.assertEqual(result, None)
            self.assertEqual(secpol.checked, (None, 1, None))
        finally:
            manager.pop()

    def test_principals_allowed_by_permission(self):
        secpol = DummySecurityPolicy(None)
        adapter = self._makeOne(secpol)
        result = adapter.principals_allowed_by_permission(None, None)
        self.assertEqual(result, ['fred', 'bob'])
        
    

class DummyContext:
    def __init__(self, *arg, **kw):
        self.__dict__.update(kw)

class DummyRequest:
    def __init__(self, environ):
        self.environ = environ


VIEW = 'view'
EDIT = 'edit'
CREATE = 'create'
DELETE = 'delete'
MODERATE = 'moderate'
ADMINISTER = 'administer'
COMMENT = 'comment'

GUEST_PERMS = (VIEW, COMMENT)
MEMBER_PERMS = GUEST_PERMS + (EDIT, CREATE, DELETE)
MODERATOR_PERMS = MEMBER_PERMS + (MODERATE,)
ADMINISTRATOR_PERMS = MODERATOR_PERMS + (ADMINISTER,)

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

