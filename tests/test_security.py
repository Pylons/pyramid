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
        reg.registerAdapter(
            checker,
            (IViewClassifier, Interface, Interface),
            ISecuredView,
            view_name,
        )
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
        request = testing.DummyRequest({})

        class DummyView(object):
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
        from pyramid.threadlocal import get_current_registry
        from pyramid.interfaces import ISettings

        settings = dict(debug_authorization=True)
        reg = get_current_registry()
        reg.registerUtility(settings, ISettings)
        context = DummyContext()
        request = testing.DummyRequest({})
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
        self.assertEquals(request.identity, None)

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

    def test_with_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        _registerSecurityPolicy(request.registry, 'wat')
        self.assertEqual(request.authenticated_userid, 'yo')

    def test_with_security_policy(self):
        request = _makeRequest()
        _registerSecurityPolicy(request.registry, 'yo')
        self.assertEqual(request.authenticated_userid, 'yo')

    def test_with_authentication_policy_no_reg_on_request(self):
        from pyramid.threadlocal import get_current_registry

        registry = get_current_registry()
        request = _makeRequest()
        del request.registry
        _registerAuthenticationPolicy(registry, 'yo')
        self.assertEqual(request.authenticated_userid, 'yo')


class TestUnAuthenticatedUserId(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_no_authentication_policy(self):
        request = _makeRequest()
        self.assertEqual(request.unauthenticated_userid, None)

    def test_with_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        _registerSecurityPolicy(request.registry, 'wat')
        self.assertEqual(request.unauthenticated_userid, 'yo')

    def test_with_security_policy(self):
        request = _makeRequest()
        _registerSecurityPolicy(request.registry, 'yo')
        self.assertEqual(request.unauthenticated_userid, 'yo')

    def test_with_authentication_policy_no_reg_on_request(self):
        from pyramid.threadlocal import get_current_registry

        registry = get_current_registry()
        request = _makeRequest()
        del request.registry
        _registerAuthenticationPolicy(registry, 'yo')
        self.assertEqual(request.unauthenticated_userid, 'yo')


class TestEffectivePrincipals(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_no_authentication_policy(self):
        from pyramid.security import Everyone

        request = _makeRequest()
        self.assertEqual(request.effective_principals, [Everyone])

    def test_with_authentication_policy(self):
        request = _makeRequest()
        _registerAuthenticationPolicy(request.registry, 'yo')
        self.assertEqual(request.effective_principals, 'yo')

    def test_with_authentication_policy_no_reg_on_request(self):
        from pyramid.threadlocal import get_current_registry

        registry = get_current_registry()
        request = _makeRequest()
        del request.registry
        _registerAuthenticationPolicy(registry, 'yo')
        self.assertEqual(request.effective_principals, 'yo')


class TestHasPermission(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self):
        from pyramid.security import SecurityAPIMixin
        from pyramid.registry import Registry

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

        self.assertEqual(policy.identify(request), 'userid')

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

    def test_permits(self):
        from pyramid.security import LegacySecurityPolicy

        request = _makeRequest()
        policy = LegacySecurityPolicy()
        _registerAuthenticationPolicy(request.registry, ['p1', 'p2'])
        _registerAuthorizationPolicy(request.registry, True)

        self.assertIs(
            policy.permits(request, request.context, 'userid', 'permission'),
            True,
        )


_TEST_HEADER = 'X-Pyramid-Test'


class DummyContext:
    def __init__(self, *arg, **kw):
        self.__dict__.update(kw)


class DummySecurityPolicy:
    def __init__(self, result):
        self.result = result

    def identify(self, request):
        return self.result

    def permits(self, request, context, identity, permission):
        return self.result

    def remember(self, request, userid, **kw):
        headers = [(_TEST_HEADER, userid)]
        self._header_remembered = headers[0]
        return headers

    def forget(self, request):
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


class TestACLHelper(unittest.TestCase):
    def test_no_acl(self):
        from pyramid.security import ACLHelper

        context = DummyContext()
        helper = ACLHelper()
        result = helper.permits(context, ['foo'], 'permission')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, '<default deny>')
        self.assertEqual(
            result.acl, '<No ACL found on any object in resource lineage>'
        )
        self.assertEqual(result.permission, 'permission')
        self.assertEqual(result.principals, ['foo'])
        self.assertEqual(result.context, context)

    def test_acl(self):
        from pyramid.security import ACLHelper
        from pyramid.security import Deny
        from pyramid.security import Allow
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
        from pyramid.security import ALL_PERMISSIONS
        from pyramid.security import DENY_ALL

        helper = ACLHelper()
        root = DummyContext()
        community = DummyContext(__name__='community', __parent__=root)
        blog = DummyContext(__name__='blog', __parent__=community)
        root.__acl__ = [(Allow, Authenticated, VIEW)]
        community.__acl__ = [
            (Allow, 'fred', ALL_PERMISSIONS),
            (Allow, 'wilma', VIEW),
            DENY_ALL,
        ]
        blog.__acl__ = [
            (Allow, 'barney', MEMBER_PERMS),
            (Allow, 'wilma', VIEW),
        ]

        result = helper.permits(
            blog, [Everyone, Authenticated, 'wilma'], 'view'
        )
        self.assertEqual(result, True)
        self.assertEqual(result.context, blog)
        self.assertEqual(result.ace, (Allow, 'wilma', VIEW))
        self.assertEqual(result.acl, blog.__acl__)

        result = helper.permits(
            blog, [Everyone, Authenticated, 'wilma'], 'delete'
        )
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

        result = helper.permits(
            blog, [Everyone, Authenticated, 'fred'], 'view'
        )
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'fred', ALL_PERMISSIONS))
        result = helper.permits(
            blog, [Everyone, Authenticated, 'fred'], 'doesntevenexistyet'
        )
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'fred', ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

        result = helper.permits(
            blog, [Everyone, Authenticated, 'barney'], 'view'
        )
        self.assertEqual(result, True)
        self.assertEqual(result.context, blog)
        self.assertEqual(result.ace, (Allow, 'barney', MEMBER_PERMS))
        result = helper.permits(
            blog, [Everyone, Authenticated, 'barney'], 'administer'
        )
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

        result = helper.permits(
            root, [Everyone, Authenticated, 'someguy'], 'view'
        )
        self.assertEqual(result, True)
        self.assertEqual(result.context, root)
        self.assertEqual(result.ace, (Allow, Authenticated, VIEW))
        result = helper.permits(
            blog, [Everyone, Authenticated, 'someguy'], 'view'
        )
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

        result = helper.permits(root, [Everyone], 'view')
        self.assertEqual(result, False)
        self.assertEqual(result.context, root)
        self.assertEqual(result.ace, '<default deny>')
        self.assertEqual(result.acl, root.__acl__)

        context = DummyContext()
        result = helper.permits(context, [Everyone], 'view')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, '<default deny>')
        self.assertEqual(
            result.acl, '<No ACL found on any object in resource lineage>'
        )

    def test_string_permissions_in_acl(self):
        from pyramid.security import ACLHelper
        from pyramid.security import Allow

        helper = ACLHelper()
        root = DummyContext()
        root.__acl__ = [(Allow, 'wilma', 'view_stuff')]

        result = helper.permits(root, ['wilma'], 'view')
        # would be True if matching against 'view_stuff' instead of against
        # ['view_stuff']
        self.assertEqual(result, False)

    def test_callable_acl(self):
        from pyramid.security import ACLHelper
        from pyramid.security import Allow

        helper = ACLHelper()
        context = DummyContext()
        fn = lambda self: [(Allow, 'bob', 'read')]
        context.__acl__ = fn.__get__(context, context.__class__)
        result = helper.permits(context, ['bob'], 'read')
        self.assertTrue(result)

    def test_principals_allowed_by_permission_direct(self):
        from pyramid.security import ACLHelper
        from pyramid.security import Allow
        from pyramid.security import DENY_ALL

        helper = ACLHelper()
        context = DummyContext()
        acl = [
            (Allow, 'chrism', ('read', 'write')),
            DENY_ALL,
            (Allow, 'other', 'read'),
        ]
        context.__acl__ = acl
        result = sorted(
            helper.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, ['chrism'])

    def test_principals_allowed_by_permission_callable_acl(self):
        from pyramid.security import ACLHelper
        from pyramid.security import Allow
        from pyramid.security import DENY_ALL

        helper = ACLHelper()
        context = DummyContext()
        acl = lambda: [
            (Allow, 'chrism', ('read', 'write')),
            DENY_ALL,
            (Allow, 'other', 'read'),
        ]
        context.__acl__ = acl
        result = sorted(
            helper.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, ['chrism'])

    def test_principals_allowed_by_permission_string_permission(self):
        from pyramid.security import ACLHelper
        from pyramid.security import Allow

        helper = ACLHelper()
        context = DummyContext()
        acl = [(Allow, 'chrism', 'read_it')]
        context.__acl__ = acl
        result = helper.principals_allowed_by_permission(context, 'read')
        # would be ['chrism'] if 'read' were compared against 'read_it' instead
        # of against ['read_it']
        self.assertEqual(list(result), [])

    def test_principals_allowed_by_permission(self):
        from pyramid.security import ACLHelper
        from pyramid.security import Allow
        from pyramid.security import Deny
        from pyramid.security import DENY_ALL
        from pyramid.security import ALL_PERMISSIONS

        helper = ACLHelper()
        root = DummyContext(__name__='', __parent__=None)
        community = DummyContext(__name__='community', __parent__=root)
        blog = DummyContext(__name__='blog', __parent__=community)
        root.__acl__ = [
            (Allow, 'chrism', ('read', 'write')),
            (Allow, 'other', ('read',)),
            (Allow, 'jim', ALL_PERMISSIONS),
        ]
        community.__acl__ = [
            (Deny, 'flooz', 'read'),
            (Allow, 'flooz', 'read'),
            (Allow, 'mork', 'read'),
            (Deny, 'jim', 'read'),
            (Allow, 'someguy', 'manage'),
        ]
        blog.__acl__ = [(Allow, 'fred', 'read'), DENY_ALL]

        result = sorted(helper.principals_allowed_by_permission(blog, 'read'))
        self.assertEqual(result, ['fred'])
        result = sorted(
            helper.principals_allowed_by_permission(community, 'read')
        )
        self.assertEqual(result, ['chrism', 'mork', 'other'])
        result = sorted(
            helper.principals_allowed_by_permission(community, 'read')
        )
        result = sorted(helper.principals_allowed_by_permission(root, 'read'))
        self.assertEqual(result, ['chrism', 'jim', 'other'])

    def test_principals_allowed_by_permission_no_acls(self):
        from pyramid.security import ACLHelper

        helper = ACLHelper()
        context = DummyContext()
        result = sorted(
            helper.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, [])

    def test_principals_allowed_by_permission_deny_not_permission_in_acl(self):
        from pyramid.security import ACLHelper
        from pyramid.security import Deny
        from pyramid.security import Everyone

        helper = ACLHelper()
        context = DummyContext()
        acl = [(Deny, Everyone, 'write')]
        context.__acl__ = acl
        result = sorted(
            helper.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, [])

    def test_principals_allowed_by_permission_deny_permission_in_acl(self):
        from pyramid.security import ACLHelper
        from pyramid.security import Deny
        from pyramid.security import Everyone

        helper = ACLHelper()
        context = DummyContext()
        acl = [(Deny, Everyone, 'read')]
        context.__acl__ = acl
        result = sorted(
            helper.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, [])


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


class TestSessionAuthenticationHelper(unittest.TestCase):
    def _makeRequest(self, session=None):
        from types import SimpleNamespace

        if session is None:
            session = dict()
        return SimpleNamespace(session=session)

    def _makeOne(self, prefix=''):
        from pyramid.security import SessionAuthenticationHelper

        return SessionAuthenticationHelper(prefix=prefix)

    def test_identify(self):
        request = self._makeRequest({'userid': 'fred'})
        helper = self._makeOne()
        self.assertEqual(helper.identify(request), 'fred')

    def test_identify_with_prefix(self):
        request = self._makeRequest({'foo.userid': 'fred'})
        helper = self._makeOne(prefix='foo.')
        self.assertEqual(helper.identify(request), 'fred')

    def test_identify_none(self):
        request = self._makeRequest()
        helper = self._makeOne()
        self.assertEqual(helper.identify(request), None)

    def test_remember(self):
        request = self._makeRequest()
        helper = self._makeOne()
        result = helper.remember(request, 'fred')
        self.assertEqual(request.session.get('userid'), 'fred')
        self.assertEqual(result, [])

    def test_forget(self):
        request = self._makeRequest({'userid': 'fred'})
        helper = self._makeOne()
        result = helper.forget(request)
        self.assertEqual(request.session.get('userid'), None)
        self.assertEqual(result, [])

    def test_forget_no_identity(self):
        request = self._makeRequest()
        helper = self._makeOne()
        result = helper.forget(request)
        self.assertEqual(request.session.get('userid'), None)
        self.assertEqual(result, [])
