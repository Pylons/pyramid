import unittest

from zope.component.testing import PlacelessSetup

class TestACLAuthorizer(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.security import ACLAuthorizer
        return ACLAuthorizer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_permits_no_acl_raises(self):
        context = DummyContext()
        logger = DummyLogger()
        authorizer = self._makeOne(context, logger)
        from repoze.bfg.interfaces import NoAuthorizationInformation
        self.assertRaises(NoAuthorizationInformation,
                          authorizer.permits, (), None)

    def test_permits_deny_implicit_empty_acl(self):
        context = DummyContext()
        logger = DummyLogger()
        context.__acl__ = []
        authorizer = self._makeOne(context, logger)
        result = authorizer.permits((), None)
        self.assertEqual(result, False)
        self.assertEqual(result.ace, None)

    def test_permits_deny_no_principals_implicit(self):
        context = DummyContext()
        logger = DummyLogger()
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Everyone
        acl = [(Allow, Everyone, 'view')]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        result = authorizer.permits(None)
        self.assertEqual(result, False)
        self.assertEqual(result.ace, None)

    def test_permits_deny_oneacl_implicit(self):
        context = DummyContext()
        logger = DummyLogger()
        from repoze.bfg.security import Allow
        acl = [(Allow, 'somebody', 'view')]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        result = authorizer.permits('view', 'somebodyelse')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, None)

    def test_permits_deny_twoacl_implicit(self):
        context = DummyContext()
        logger = DummyLogger()
        from repoze.bfg.security import Allow
        acl = [(Allow, 'somebody', 'view'), (Allow, 'somebody', 'write')]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        result = authorizer.permits('view', 'somebodyelse')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, None)

    def test_permits_deny_oneacl_explcit(self):
        context = DummyContext()
        logger = DummyLogger()
        from repoze.bfg.security import Deny
        ace = (Deny, 'somebody', 'view')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        result = authorizer.permits('view', 'somebody')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, ace)

    def test_permits_deny_oneacl_multiperm_explcit(self):
        context = DummyContext()
        logger = DummyLogger()
        acl = []
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Allow
        deny = (Deny, 'somebody', ('view', 'read'))
        allow = (Allow, 'somebody', 'view')
        acl = [deny, allow]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        result = authorizer.permits('view', 'somebody')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, deny)

    def test_permits_deny_twoacl_explicit(self):
        context = DummyContext()
        logger = DummyLogger()
        acl = []
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Allow
        allow = (Allow, 'somebody', 'read')
        deny = (Deny, 'somebody', 'view')
        acl = [allow, deny]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        result = authorizer.permits('view', 'somebody')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, deny)

    def test_permits_allow_twoacl_explicit(self):
        context = DummyContext()
        logger = DummyLogger()
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Allow
        allow = (Allow, 'somebody', 'read')
        deny = (Deny, 'somebody', 'view')
        acl = [allow, deny]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        result = authorizer.permits('read', 'somebody')
        self.assertEqual(result, True)
        self.assertEqual(result.ace, allow)

    def test_permits_nested_principals_list_allow(self):
        context = DummyContext()
        logger = DummyLogger()
        acl = []
        from repoze.bfg.security import Allow
        ace = (Allow, 'larry', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        principals = (['fred', ['jim', ['bob', 'larry']]])
        result = authorizer.permits('read', *principals)
        self.assertEqual(result, True)
        self.assertEqual(result.ace, ace)

    def test_permits_nested_principals_list_deny_explicit(self):
        context = DummyContext()
        logger = DummyLogger()
        from repoze.bfg.security import Deny
        ace = (Deny, 'larry', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        principals = (['fred', ['jim', ['bob', 'larry']]])
        result = authorizer.permits('read', *principals)
        self.assertEqual(result, False)
        self.assertEqual(result.ace, ace)

    def test_permits_nested_principals_list_deny_implicit(self):
        context = DummyContext()
        logger = DummyLogger()
        from repoze.bfg.security import Allow
        ace = (Allow, 'somebodyelse', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        principals = (['fred', ['jim', ['bob', 'larry']]])
        result = authorizer.permits('read', *principals)
        self.assertEqual(result, False)

    def test_permits_allow_via_location_parent(self):
        context = DummyContext()
        context.__parent__ = None
        context.__name__ = None
        logger = DummyLogger()
        from repoze.bfg.security import Allow
        ace = (Allow, 'fred', 'read')
        acl = [ace]
        context.__acl__ = acl
        context2 = DummyContext()
        context2.__parent__ = context
        context2.__name__ = 'myname'
        authorizer = self._makeOne(context, logger)
        principals = ['fred']
        result = authorizer.permits('read', *principals)
        self.assertEqual(result, True)

    def test_logging_deny_implicit(self):
        context = DummyContext()
        logger = DummyLogger()
        from repoze.bfg.security import Allow
        ace = (Allow, 'somebodyelse', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        principals = ['fred']
        result = authorizer.permits('read', *principals)
        self.assertEqual(len(logger.messages), 1)

    def test_logging_deny_explicit(self):
        context = DummyContext()
        logger = DummyLogger()
        from repoze.bfg.security import Deny
        ace = (Deny, 'somebodyelse', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        principals = ['somebodyelse']
        result = authorizer.permits('read', *principals)
        self.assertEqual(len(logger.messages), 1)

    def test_logging_allow(self):
        context = DummyContext()
        logger = DummyLogger()
        from repoze.bfg.security import Allow
        ace = (Allow, 'somebodyelse', 'read')
        acl = [ace]
        context.__acl__ = acl
        authorizer = self._makeOne(context, logger)
        principals = ['somebodyelse']
        result = authorizer.permits('read', *principals)
        self.assertEqual(len(logger.messages), 1)

class RemoteUserACLSecurityPolicy(unittest.TestCase, PlacelessSetup):
    def _getTargetClass(self):
        from repoze.bfg.security import RemoteUserACLSecurityPolicy
        return RemoteUserACLSecurityPolicy

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def test_authenticated_userid(self):
        context = DummyContext()
        request = DummyRequest({'REMOTE_USER':'fred'})
        logger = DummyLogger()
        policy = self._makeOne(logger)
        result = policy.authenticated_userid(request)
        self.assertEqual(result, 'fred')

    def test_effective_principals(self):
        context = DummyContext()
        request = DummyRequest({'REMOTE_USER':'fred'})
        logger = DummyLogger()
        policy = self._makeOne(logger)
        result = policy.effective_principals(request)
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        self.assertEqual(result, [Everyone, Authenticated, 'fred'])

    def test_permits_no_remote_user_no_acl_info_on_context(self):
        context = DummyContext()
        request = DummyRequest({})
        logger = DummyLogger()
        policy = self._makeOne(logger)
        authorizer_factory = make_authorizer_factory(None)
        policy.authorizer_factory = authorizer_factory
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        from repoze.bfg.security import Everyone
        self.assertEqual(authorizer_factory.principals, (Everyone,))
        self.assertEqual(authorizer_factory.permission, 'view')
        self.assertEqual(authorizer_factory.context, context)

    def test_permits_no_remote_user_acl_info_on_context(self):
        context = DummyContext()
        context.__acl__ = []
        request = DummyRequest({})
        logger = DummyLogger()
        policy = self._makeOne(logger)
        authorizer_factory = make_authorizer_factory(None)
        policy.authorizer_factory = authorizer_factory
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        from repoze.bfg.security import Everyone
        self.assertEqual(authorizer_factory.principals, (Everyone,))
        self.assertEqual(authorizer_factory.permission, 'view')
        self.assertEqual(authorizer_factory.context, context)

    def test_permits_no_remote_user_withparents_root_has_acl_info(self):
        context = DummyContext()
        context.__name__ = None
        context.__parent__ = None
        context2 = DummyContext()
        context2.__name__ = 'context2'
        context2.__parent__ = context
        context.__acl__ = []
        request = DummyRequest({})
        logger = DummyLogger()
        policy = self._makeOne(logger)
        authorizer_factory = make_authorizer_factory(None)
        policy.authorizer_factory = authorizer_factory
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        from repoze.bfg.security import Everyone
        self.assertEqual(authorizer_factory.principals, (Everyone,))
        self.assertEqual(authorizer_factory.permission, 'view')
        self.assertEqual(authorizer_factory.context, context)

    def test_permits_no_remote_user_withparents_root_allows_everyone(self):
        context = DummyContext()
        context.__name__ = None
        context.__parent__ = None
        context2 = DummyContext()
        context2.__name__ = 'context2'
        context2.__parent__ = context
        request = DummyRequest({})
        logger = DummyLogger()
        policy = self._makeOne(logger)
        authorizer_factory = make_authorizer_factory(context)
        policy.authorizer_factory = authorizer_factory
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, True)
        from repoze.bfg.security import Everyone
        self.assertEqual(authorizer_factory.principals, (Everyone,))
        self.assertEqual(authorizer_factory.permission, 'view')
        self.assertEqual(authorizer_factory.context, context)

class TestHasPermission(unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.security import has_permission
        return has_permission

    def _registerSecurityPolicy(self, secpol):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import ISecurityPolicy
        gsm.registerUtility(secpol, ISecurityPolicy)

    def test_registered(self):
        secpol = DummySecurityPolicy(False)
        self._registerSecurityPolicy(secpol)
        has_permission = self._getFUT()
        self.assertEqual(has_permission('view', None, None), False)
        
    def test_not_registered(self):
        has_permission = self._getFUT()
        self.assertEqual(has_permission('view', None, None), True)


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

class DummyLogger:
    def __init__(self):
        self.messages = []
    def debug(self, msg):
        self.messages.append(msg)

class make_authorizer_factory:
    def __init__(self, expected_context, intermediates_raise=False):
        self.expected_context = expected_context
        self.intermediates_raise = intermediates_raise

    def __call__(self, context, logger):
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

    


            
                
    
        

    
