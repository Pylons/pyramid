import unittest
import warnings
from http.cookies import SimpleCookie

from pyramid import testing
from pyramid.util import text_


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


class TestAuthTicket(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.security import AuthTicket

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

    def test_digest_sha512(self):
        ticket = self._makeOne(
            'secret', 'userid', '0.0.0.0', time=10, hashalg='sha512'
        )
        result = ticket.digest()
        self.assertEqual(
            result,
            '74770b2e0d5b1a54c2a466ec567a40f7d7823576aa49'
            '3c65fc3445e9b44097f4a80410319ef8cb256a2e60b9'
            'c2002e48a9e33a3e8ee4379352c04ef96d2cb278',
        )

    def test_cookie_value(self):
        ticket = self._makeOne(
            'secret', 'userid', '0.0.0.0', time=10, tokens=('a', 'b')
        )
        result = ticket.cookie_value()
        self.assertEqual(
            result, '66f9cc3e423dc57c91df696cf3d1f0d80000000auserid!a,b!'
        )

    def test_ipv4(self):
        ticket = self._makeOne(
            'secret', 'userid', '198.51.100.1', time=10, hashalg='sha256'
        )
        result = ticket.cookie_value()
        self.assertEqual(
            result,
            'b3e7156db4f8abde4439c4a6499a0668f9e7ffd7fa27b'
            '798400ecdade8d76c530000000auserid!',
        )

    def test_ipv6(self):
        ticket = self._makeOne(
            'secret', 'userid', '2001:db8::1', time=10, hashalg='sha256'
        )
        result = ticket.cookie_value()
        self.assertEqual(
            result,
            'd025b601a0f12ca6d008aa35ff3a22b7d8f3d1c1456c8'
            '5becf8760cd7a2fa4910000000auserid!',
        )


class TestBadTicket(unittest.TestCase):
    def _makeOne(self, msg, expected=None):
        from pyramid.security import BadTicket

        return BadTicket(msg, expected)

    def test_it(self):
        exc = self._makeOne('msg', expected=True)
        self.assertEqual(exc.expected, True)
        self.assertTrue(isinstance(exc, Exception))


class Test_parse_ticket(unittest.TestCase):
    def _callFUT(self, secret, ticket, ip, hashalg='md5'):
        from pyramid.security import parse_ticket

        return parse_ticket(secret, ticket, ip, hashalg)

    def _assertRaisesBadTicket(self, secret, ticket, ip, hashalg='md5'):
        from pyramid.security import BadTicket

        self.assertRaises(
            BadTicket, self._callFUT, secret, ticket, ip, hashalg
        )

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
        ticket = text_('66f9cc3e423dc57c91df696cf3d1f0d80000000auserid!a,b!')
        result = self._callFUT('secret', ticket, '0.0.0.0')
        self.assertEqual(result, (10, 'userid', ['a', 'b'], ''))

    def test_correct_with_user_data_sha512(self):
        ticket = text_(
            '7d947cdef99bad55f8e3382a8bd089bb9dd0547f7925b7d189adc1'
            '160cab0ec0e6888faa41eba641a18522b26f19109f3ffafb769767'
            'ba8a26d02aaeae56599a0000000auserid!a,b!'
        )
        result = self._callFUT('secret', ticket, '0.0.0.0', 'sha512')
        self.assertEqual(result, (10, 'userid', ['a', 'b'], ''))

    def test_ipv4(self):
        ticket = text_(
            'b3e7156db4f8abde4439c4a6499a0668f9e7ffd7fa27b798400ecd'
            'ade8d76c530000000auserid!'
        )
        result = self._callFUT('secret', ticket, '198.51.100.1', 'sha256')
        self.assertEqual(result, (10, 'userid', [''], ''))

    def test_ipv6(self):
        ticket = text_(
            'd025b601a0f12ca6d008aa35ff3a22b7d8f3d1c1456c85becf8760'
            'cd7a2fa4910000000auserid!'
        )
        result = self._callFUT('secret', ticket, '2001:db8::1', 'sha256')
        self.assertEqual(result, (10, 'userid', [''], ''))


class TestAuthTktCookieHelper(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.security import AuthTktCookieHelper

        return AuthTktCookieHelper

    def _makeOne(self, *arg, **kw):
        helper = self._getTargetClass()(*arg, **kw)
        auth_tkt = DummyAuthTktModule()
        helper.auth_tkt = auth_tkt
        helper.AuthTicket = auth_tkt.AuthTicket
        helper.parse_ticket = auth_tkt.parse_ticket
        helper.BadTicket = auth_tkt.BadTicket
        return helper

    def _makeRequest(self, cookie=None, ipv6=False):
        environ = {'wsgi.version': (1, 0)}

        if ipv6 is False:
            environ['REMOTE_ADDR'] = '1.1.1.1'
        else:
            environ['REMOTE_ADDR'] = '::1'
        environ['SERVER_NAME'] = 'localhost'
        return DummyRequest(environ, cookie=cookie)

    def _cookieValue(self, cookie):
        items = cookie.value.split('/')
        D = {}
        for item in items:
            k, v = item.split('=', 1)
            D[k] = v
        return D

    def _parseHeaders(self, headers):
        return [self._parseHeader(header) for header in headers]

    def _parseHeader(self, header):
        cookie = self._parseCookie(header[1])
        return cookie

    def _parseCookie(self, cookie):
        cookies = SimpleCookie()
        cookies.load(cookie)
        return cookies.get('auth_tkt')

    def test_init_cookie_str_reissue_invalid(self):
        self.assertRaises(
            ValueError, self._makeOne, 'secret', reissue_time='invalid value'
        )

    def test_init_cookie_str_timeout_invalid(self):
        self.assertRaises(
            ValueError, self._makeOne, 'secret', timeout='invalid value'
        )

    def test_init_cookie_str_max_age_invalid(self):
        self.assertRaises(
            ValueError, self._makeOne, 'secret', max_age='invalid value'
        )

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
        self.assertEqual(environ['REMOTE_USER_DATA'], '')
        self.assertEqual(environ['AUTH_TYPE'], 'cookie')

    def test_identify_good_cookie_include_ipv6(self):
        helper = self._makeOne('secret', include_ip=True)
        request = self._makeRequest('ticket', ipv6=True)
        result = helper.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], 'userid')
        self.assertEqual(result['userdata'], '')
        self.assertEqual(result['timestamp'], 0)
        self.assertEqual(helper.auth_tkt.value, 'ticket')
        self.assertEqual(helper.auth_tkt.remote_addr, '::1')
        self.assertEqual(helper.auth_tkt.secret, 'secret')
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'], '')
        self.assertEqual(environ['AUTH_TYPE'], 'cookie')

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
        self.assertEqual(environ['REMOTE_USER_DATA'], '')
        self.assertEqual(environ['AUTH_TYPE'], 'cookie')

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
        self.assertEqual(environ['REMOTE_USER_DATA'], 'userid_type:int')
        self.assertEqual(environ['AUTH_TYPE'], 'cookie')

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
        self.assertEqual(environ['REMOTE_USER_DATA'], 'bogus:int')
        self.assertEqual(environ['AUTH_TYPE'], 'cookie')

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
        self.assertEqual(environ['REMOTE_USER_DATA'], 'userid_type:unknown')
        self.assertEqual(environ['AUTH_TYPE'], 'cookie')

    def test_identify_good_cookie_b64str_useridtype(self):
        from base64 import b64encode

        helper = self._makeOne('secret', include_ip=False)
        helper.auth_tkt.userid = b64encode(b'encoded').strip()
        helper.auth_tkt.user_data = 'userid_type:b64str'
        request = self._makeRequest('ticket')
        result = helper.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], b'encoded')
        self.assertEqual(result['userdata'], 'userid_type:b64str')
        self.assertEqual(result['timestamp'], 0)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'], 'userid_type:b64str')
        self.assertEqual(environ['AUTH_TYPE'], 'cookie')

    def test_identify_good_cookie_b64unicode_useridtype(self):
        from base64 import b64encode

        helper = self._makeOne('secret', include_ip=False)
        helper.auth_tkt.userid = b64encode(b'\xc3\xa9ncoded').strip()
        helper.auth_tkt.user_data = 'userid_type:b64unicode'
        request = self._makeRequest('ticket')
        result = helper.identify(request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['tokens'], ())
        self.assertEqual(result['userid'], text_(b'\xc3\xa9ncoded', 'utf-8'))
        self.assertEqual(result['userdata'], 'userid_type:b64unicode')
        self.assertEqual(result['timestamp'], 0)
        environ = request.environ
        self.assertEqual(environ['REMOTE_USER_TOKENS'], ())
        self.assertEqual(environ['REMOTE_USER_DATA'], 'userid_type:b64unicode')
        self.assertEqual(environ['AUTH_TYPE'], 'cookie')

    def test_identify_bad_cookie(self):
        helper = self._makeOne('secret', include_ip=True)
        helper.auth_tkt.parse_raise = True
        request = self._makeRequest('ticket')
        result = helper.identify(request)
        self.assertEqual(result, None)

    def test_identify_cookie_timeout(self):
        helper = self._makeOne('secret', timeout=1)
        self.assertEqual(helper.timeout, 1)

    def test_identify_cookie_str_timeout(self):
        helper = self._makeOne('secret', timeout='1')
        self.assertEqual(helper.timeout, 1)

    def test_identify_cookie_timeout_aged(self):
        import time

        helper = self._makeOne('secret', timeout=10)
        now = time.time()
        helper.auth_tkt.timestamp = now - 1
        helper.now = now + 10
        helper.auth_tkt.tokens = (text_('a'),)
        request = self._makeRequest('bogus')
        result = helper.identify(request)
        self.assertFalse(result)

    def test_identify_cookie_reissue(self):
        import time

        helper = self._makeOne('secret', timeout=10, reissue_time=0)
        now = time.time()
        helper.auth_tkt.timestamp = now
        helper.now = now + 1
        helper.auth_tkt.tokens = (text_('a'),)
        request = self._makeRequest('bogus')
        result = helper.identify(request)
        self.assertTrue(result)
        self.assertEqual(len(request.callbacks), 1)
        response = DummyResponse()
        request.callbacks[0](request, response)
        self.assertEqual(len(response.headerlist), 3)
        self.assertEqual(response.headerlist[0][0], 'Set-Cookie')

    def test_identify_cookie_str_reissue(self):
        import time

        helper = self._makeOne('secret', timeout=10, reissue_time='0')
        now = time.time()
        helper.auth_tkt.timestamp = now
        helper.now = now + 1
        helper.auth_tkt.tokens = (text_('a'),)
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
        self.assertTrue("/tokens=/" in response.headerlist[0][1])

    def test_remember(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, 'userid')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; Path=/; SameSite=Lax'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(
            result[1][1].endswith('; Domain=localhost; Path=/; SameSite=Lax')
        )
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue(
            result[2][1].endswith('; Domain=.localhost; Path=/; SameSite=Lax')
        )
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_nondefault_samesite(self):
        helper = self._makeOne('secret', samesite='Strict')
        request = self._makeRequest()
        result = helper.remember(request, 'userid')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; Path=/; SameSite=Strict'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(
            result[1][1].endswith(
                '; Domain=localhost; Path=/; SameSite=Strict'
            )
        )
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue(
            result[2][1].endswith(
                '; Domain=.localhost; Path=/; SameSite=Strict'
            )
        )
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_None_samesite(self):
        helper = self._makeOne('secret', samesite=None)
        request = self._makeRequest()
        result = helper.remember(request, 'userid')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; Path=/'))  # no samesite
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(result[1][1].endswith('; Domain=localhost; Path=/'))
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue(result[2][1].endswith('; Domain=.localhost; Path=/'))
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_include_ip(self):
        helper = self._makeOne('secret', include_ip=True)
        request = self._makeRequest()
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; Path=/; SameSite=Lax'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(
            result[1][1].endswith('; Domain=localhost; Path=/; SameSite=Lax')
        )
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue(
            result[2][1].endswith('; Domain=.localhost; Path=/; SameSite=Lax')
        )
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_path(self):
        helper = self._makeOne(
            'secret', include_ip=True, path="/cgi-bin/app.cgi/"
        )
        request = self._makeRequest()
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(
            result[0][1].endswith('; Path=/cgi-bin/app.cgi/; SameSite=Lax')
        )
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(
            result[1][1].endswith(
                '; Domain=localhost; Path=/cgi-bin/app.cgi/; SameSite=Lax'
            )
        )
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue(
            result[2][1].endswith(
                '; Domain=.localhost; Path=/cgi-bin/app.cgi/; SameSite=Lax'
            )
        )
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_http_only(self):
        helper = self._makeOne('secret', include_ip=True, http_only=True)
        request = self._makeRequest()
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; HttpOnly; SameSite=Lax'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue('; HttpOnly' in result[1][1])
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue('; HttpOnly' in result[2][1])
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_secure(self):
        helper = self._makeOne('secret', include_ip=True, secure=True)
        request = self._makeRequest()
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue('; secure' in result[0][1])
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue('; secure' in result[1][1])
        self.assertTrue(result[1][1].startswith('auth_tkt='))

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue('; secure' in result[2][1])
        self.assertTrue(result[2][1].startswith('auth_tkt='))

    def test_remember_wild_domain_disabled(self):
        helper = self._makeOne('secret', wild_domain=False)
        request = self._makeRequest()
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(result[0][1].endswith('; Path=/; SameSite=Lax'))
        self.assertTrue(result[0][1].startswith('auth_tkt='))

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue(
            result[1][1].endswith('; Domain=localhost; Path=/; SameSite=Lax')
        )
        self.assertTrue(result[1][1].startswith('auth_tkt='))

    def test_remember_parent_domain(self):
        helper = self._makeOne('secret', parent_domain=True)
        request = self._makeRequest()
        request.domain = 'www.example.com'
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 1)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(
            result[0][1].endswith(
                '; Domain=.example.com; Path=/; SameSite=Lax'
            )
        )
        self.assertTrue(result[0][1].startswith('auth_tkt='))

    def test_remember_parent_domain_supercedes_wild_domain(self):
        helper = self._makeOne('secret', parent_domain=True, wild_domain=True)
        request = self._makeRequest()
        request.domain = 'www.example.com'
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 1)
        self.assertTrue(
            result[0][1].endswith(
                '; Domain=.example.com; Path=/; SameSite=Lax'
            )
        )

    def test_remember_explicit_domain(self):
        helper = self._makeOne('secret', domain='pyramid.bazinga')
        request = self._makeRequest()
        request.domain = 'www.example.com'
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 1)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue(
            result[0][1].endswith(
                '; Domain=pyramid.bazinga; Path=/; SameSite=Lax'
            )
        )
        self.assertTrue(result[0][1].startswith('auth_tkt='))

    def test_remember_domain_supercedes_parent_and_wild_domain(self):
        helper = self._makeOne(
            'secret',
            domain='pyramid.bazinga',
            parent_domain=True,
            wild_domain=True,
        )
        request = self._makeRequest()
        request.domain = 'www.example.com'
        result = helper.remember(request, 'other')
        self.assertEqual(len(result), 1)
        self.assertTrue(
            result[0][1].endswith(
                '; Domain=pyramid.bazinga; Path=/; SameSite=Lax'
            )
        )

    def test_remember_binary_userid(self):
        import base64

        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, b'userid')
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        val = self._cookieValue(values[0])
        self.assertEqual(
            val['userid'], text_(base64.b64encode(b'userid').strip())
        )
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

    def test_remember_unicode_userid(self):
        import base64

        helper = self._makeOne('secret')
        request = self._makeRequest()
        userid = text_(b'\xc2\xa9', 'utf-8')
        result = helper.remember(request, userid)
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        val = self._cookieValue(values[0])
        self.assertEqual(
            val['userid'], text_(base64.b64encode(userid.encode('utf-8')))
        )
        self.assertEqual(val['user_data'], 'userid_type:b64unicode')

    def test_remember_insane_userid(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        userid = object()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always', RuntimeWarning)
            result = helper.remember(request, userid)
            self.assertTrue(str(w[-1].message).startswith('userid is of type'))
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)
        value = values[0]
        self.assertTrue('userid' in value.value)

    def test_remember_max_age(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, 'userid', max_age=500)
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)

        self.assertEqual(values[0]['max-age'], '500')
        self.assertTrue(values[0]['expires'])

    def test_remember_str_max_age(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, 'userid', max_age='500')
        values = self._parseHeaders(result)
        self.assertEqual(len(result), 3)

        self.assertEqual(values[0]['max-age'], '500')
        self.assertTrue(values[0]['expires'])

    def test_remember_str_max_age_invalid(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        self.assertRaises(
            ValueError,
            helper.remember,
            request,
            'userid',
            max_age='invalid value',
        )

    def test_remember_tokens(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, 'other', tokens=('foo', 'bar'))
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        self.assertTrue("/tokens=foo|bar/" in result[0][1])

        self.assertEqual(result[1][0], 'Set-Cookie')
        self.assertTrue("/tokens=foo|bar/" in result[1][1])

        self.assertEqual(result[2][0], 'Set-Cookie')
        self.assertTrue("/tokens=foo|bar/" in result[2][1])

    def test_remember_samesite_nondefault(self):
        helper = self._makeOne('secret', samesite='Strict')
        request = self._makeRequest()
        result = helper.remember(request, 'userid')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        cookieval = result[0][1]
        self.assertTrue(
            'SameSite=Strict' in [x.strip() for x in cookieval.split(';')],
            cookieval,
        )

        self.assertEqual(result[1][0], 'Set-Cookie')
        cookieval = result[1][1]
        self.assertTrue(
            'SameSite=Strict' in [x.strip() for x in cookieval.split(';')],
            cookieval,
        )

        self.assertEqual(result[2][0], 'Set-Cookie')
        cookieval = result[2][1]
        self.assertTrue(
            'SameSite=Strict' in [x.strip() for x in cookieval.split(';')],
            cookieval,
        )

    def test_remember_samesite_default(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        result = helper.remember(request, 'userid')
        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], 'Set-Cookie')
        cookieval = result[0][1]
        self.assertTrue(
            'SameSite=Lax' in [x.strip() for x in cookieval.split(';')],
            cookieval,
        )

        self.assertEqual(result[1][0], 'Set-Cookie')
        cookieval = result[1][1]
        self.assertTrue(
            'SameSite=Lax' in [x.strip() for x in cookieval.split(';')],
            cookieval,
        )

        self.assertEqual(result[2][0], 'Set-Cookie')
        cookieval = result[2][1]
        self.assertTrue(
            'SameSite=Lax' in [x.strip() for x in cookieval.split(';')],
            cookieval,
        )

    def test_remember_unicode_but_ascii_token(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        la = text_(b'foo', 'utf-8')
        result = helper.remember(request, 'other', tokens=(la,))
        # tokens must be str type on both Python 2 and 3
        self.assertTrue("/tokens=foo/" in result[0][1])

    def test_remember_nonascii_token(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        la = text_(b'La Pe\xc3\xb1a', 'utf-8')
        self.assertRaises(
            ValueError, helper.remember, request, 'other', tokens=(la,)
        )

    def test_remember_invalid_token_format(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        self.assertRaises(
            ValueError, helper.remember, request, 'other', tokens=('foo bar',)
        )
        self.assertRaises(
            ValueError, helper.remember, request, 'other', tokens=('1bar',)
        )

    def test_forget(self):
        helper = self._makeOne('secret')
        request = self._makeRequest()
        headers = helper.forget(request)
        self.assertEqual(len(headers), 3)
        name, value = headers[0]
        self.assertEqual(name, 'Set-Cookie')
        self.assertEqual(
            value,
            'auth_tkt=; Max-Age=0; Path=/; '
            'expires=Wed, 31-Dec-97 23:59:59 GMT; SameSite=Lax',
        )
        name, value = headers[1]
        self.assertEqual(name, 'Set-Cookie')
        self.assertEqual(
            value,
            'auth_tkt=; Domain=localhost; Max-Age=0; Path=/; '
            'expires=Wed, 31-Dec-97 23:59:59 GMT; SameSite=Lax',
        )
        name, value = headers[2]
        self.assertEqual(name, 'Set-Cookie')
        self.assertEqual(
            value,
            'auth_tkt=; Domain=.localhost; Max-Age=0; Path=/; '
            'expires=Wed, 31-Dec-97 23:59:59 GMT; SameSite=Lax',
        )


class DummyAuthTktModule(object):
    def __init__(
        self,
        timestamp=0,
        userid='userid',
        tokens=(),
        user_data='',
        parse_raise=False,
        hashalg="md5",
    ):
        self.timestamp = timestamp
        self.userid = userid
        self.tokens = tokens
        self.user_data = user_data
        self.parse_raise = parse_raise
        self.hashalg = hashalg

        def parse_ticket(secret, value, remote_addr, hashalg):
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
                result = {
                    'secret': self.secret,
                    'userid': self.userid,
                    'remote_addr': self.remote_addr,
                }
                result.update(self.kw)
                tokens = result.pop('tokens', None)
                if tokens is not None:
                    tokens = '|'.join(tokens)
                    result['tokens'] = tokens
                items = sorted(result.items())
                new_items = []
                for k, v in items:
                    if isinstance(v, bytes):
                        v = text_(v)
                    new_items.append((k, v))
                result = '/'.join(['%s=%s' % (k, v) for k, v in new_items])
                return result

        self.AuthTicket = AuthTicket

    class BadTicket(Exception):
        pass


class DummyCookies(object):
    def __init__(self, cookie):
        self.cookie = cookie

    def get(self, name):
        return self.cookie


class DummyRequest:
    domain = 'localhost'

    def __init__(self, environ=None, session=None, registry=None, cookie=None):
        self.environ = environ or {}
        self.session = session or {}
        self.registry = registry
        self.callbacks = []
        self.cookies = DummyCookies(cookie)

    def add_response_callback(self, callback):
        self.callbacks.append(callback)


class DummyResponse:
    def __init__(self):
        self.headerlist = []
