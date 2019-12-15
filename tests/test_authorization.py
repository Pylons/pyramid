import unittest

from pyramid.testing import cleanUp


class TestACLAuthorizationPolicy(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from pyramid.authorization import ACLAuthorizationPolicy

        return ACLAuthorizationPolicy

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_implements_IAuthorizationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthorizationPolicy

        verifyClass(IAuthorizationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthorizationPolicy(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IAuthorizationPolicy

        verifyObject(IAuthorizationPolicy, self._makeOne())

    def test_permits_no_acl(self):
        context = DummyContext()
        policy = self._makeOne()
        self.assertEqual(policy.permits(context, [], 'view'), False)

    def test_permits(self):
        from pyramid.security import Deny
        from pyramid.security import Allow
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
        from pyramid.security import ALL_PERMISSIONS
        from pyramid.security import DENY_ALL

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

        policy = self._makeOne()

        result = policy.permits(
            blog, [Everyone, Authenticated, 'wilma'], 'view'
        )
        self.assertEqual(result, True)
        self.assertEqual(result.context, blog)
        self.assertEqual(result.ace, (Allow, 'wilma', VIEW))
        self.assertEqual(result.acl, blog.__acl__)

        result = policy.permits(
            blog, [Everyone, Authenticated, 'wilma'], 'delete'
        )
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

        result = policy.permits(
            blog, [Everyone, Authenticated, 'fred'], 'view'
        )
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'fred', ALL_PERMISSIONS))
        result = policy.permits(
            blog, [Everyone, Authenticated, 'fred'], 'doesntevenexistyet'
        )
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'fred', ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

        result = policy.permits(
            blog, [Everyone, Authenticated, 'barney'], 'view'
        )
        self.assertEqual(result, True)
        self.assertEqual(result.context, blog)
        self.assertEqual(result.ace, (Allow, 'barney', MEMBER_PERMS))
        result = policy.permits(
            blog, [Everyone, Authenticated, 'barney'], 'administer'
        )
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

        result = policy.permits(
            root, [Everyone, Authenticated, 'someguy'], 'view'
        )
        self.assertEqual(result, True)
        self.assertEqual(result.context, root)
        self.assertEqual(result.ace, (Allow, Authenticated, VIEW))
        result = policy.permits(
            blog, [Everyone, Authenticated, 'someguy'], 'view'
        )
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

        result = policy.permits(root, [Everyone], 'view')
        self.assertEqual(result, False)
        self.assertEqual(result.context, root)
        self.assertEqual(result.ace, '<default deny>')
        self.assertEqual(result.acl, root.__acl__)

        context = DummyContext()
        result = policy.permits(context, [Everyone], 'view')
        self.assertEqual(result, False)
        self.assertEqual(result.ace, '<default deny>')
        self.assertEqual(
            result.acl, '<No ACL found on any object in resource lineage>'
        )

    def test_permits_string_permissions_in_acl(self):
        from pyramid.security import Allow

        root = DummyContext()
        root.__acl__ = [(Allow, 'wilma', 'view_stuff')]

        policy = self._makeOne()

        result = policy.permits(root, ['wilma'], 'view')
        # would be True if matching against 'view_stuff' instead of against
        # ['view_stuff']
        self.assertEqual(result, False)

    def test_principals_allowed_by_permission_direct(self):
        from pyramid.security import Allow
        from pyramid.security import DENY_ALL

        context = DummyContext()
        acl = [
            (Allow, 'chrism', ('read', 'write')),
            DENY_ALL,
            (Allow, 'other', 'read'),
        ]
        context.__acl__ = acl
        policy = self._makeOne()
        result = sorted(
            policy.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, ['chrism'])

    def test_principals_allowed_by_permission_callable_acl(self):
        from pyramid.security import Allow
        from pyramid.security import DENY_ALL

        context = DummyContext()
        acl = lambda: [
            (Allow, 'chrism', ('read', 'write')),
            DENY_ALL,
            (Allow, 'other', 'read'),
        ]
        context.__acl__ = acl
        policy = self._makeOne()
        result = sorted(
            policy.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, ['chrism'])

    def test_principals_allowed_by_permission_string_permission(self):
        from pyramid.security import Allow

        context = DummyContext()
        acl = [(Allow, 'chrism', 'read_it')]
        context.__acl__ = acl
        policy = self._makeOne()
        result = policy.principals_allowed_by_permission(context, 'read')
        # would be ['chrism'] if 'read' were compared against 'read_it' instead
        # of against ['read_it']
        self.assertEqual(list(result), [])

    def test_principals_allowed_by_permission(self):
        from pyramid.security import Allow
        from pyramid.security import Deny
        from pyramid.security import DENY_ALL
        from pyramid.security import ALL_PERMISSIONS

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

        policy = self._makeOne()

        result = sorted(policy.principals_allowed_by_permission(blog, 'read'))
        self.assertEqual(result, ['fred'])
        result = sorted(
            policy.principals_allowed_by_permission(community, 'read')
        )
        self.assertEqual(result, ['chrism', 'mork', 'other'])
        result = sorted(
            policy.principals_allowed_by_permission(community, 'read')
        )
        result = sorted(policy.principals_allowed_by_permission(root, 'read'))
        self.assertEqual(result, ['chrism', 'jim', 'other'])

    def test_principals_allowed_by_permission_no_acls(self):
        context = DummyContext()
        policy = self._makeOne()
        result = sorted(
            policy.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, [])

    def test_principals_allowed_by_permission_deny_not_permission_in_acl(self):
        from pyramid.security import Deny
        from pyramid.security import Everyone

        context = DummyContext()
        acl = [(Deny, Everyone, 'write')]
        context.__acl__ = acl
        policy = self._makeOne()
        result = sorted(
            policy.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, [])

    def test_principals_allowed_by_permission_deny_permission_in_acl(self):
        from pyramid.security import Deny
        from pyramid.security import Everyone

        context = DummyContext()
        acl = [(Deny, Everyone, 'read')]
        context.__acl__ = acl
        policy = self._makeOne()
        result = sorted(
            policy.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, [])

    def test_callable_acl(self):
        from pyramid.security import Allow

        context = DummyContext()
        fn = lambda self: [(Allow, 'bob', 'read')]
        context.__acl__ = fn.__get__(context, context.__class__)
        policy = self._makeOne()
        result = policy.permits(context, ['bob'], 'read')
        self.assertTrue(result)


class TestACLHelper(unittest.TestCase):
    def test_no_acl(self):
        from pyramid.authorization import ACLHelper

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
        from pyramid.authorization import ACLHelper
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
        from pyramid.authorization import ACLHelper
        from pyramid.security import Allow

        helper = ACLHelper()
        root = DummyContext()
        root.__acl__ = [(Allow, 'wilma', 'view_stuff')]

        result = helper.permits(root, ['wilma'], 'view')
        # would be True if matching against 'view_stuff' instead of against
        # ['view_stuff']
        self.assertEqual(result, False)

    def test_callable_acl(self):
        from pyramid.authorization import ACLHelper
        from pyramid.security import Allow

        helper = ACLHelper()
        context = DummyContext()
        fn = lambda self: [(Allow, 'bob', 'read')]
        context.__acl__ = fn.__get__(context, context.__class__)
        result = helper.permits(context, ['bob'], 'read')
        self.assertTrue(result)

    def test_principals_allowed_by_permission_direct(self):
        from pyramid.authorization import ACLHelper
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
        from pyramid.authorization import ACLHelper
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
        from pyramid.authorization import ACLHelper
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
        from pyramid.authorization import ACLHelper
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
        from pyramid.authorization import ACLHelper

        helper = ACLHelper()
        context = DummyContext()
        result = sorted(
            helper.principals_allowed_by_permission(context, 'read')
        )
        self.assertEqual(result, [])

    def test_principals_allowed_by_permission_deny_not_permission_in_acl(self):
        from pyramid.authorization import ACLHelper
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
        from pyramid.authorization import ACLHelper
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


class DummyContext:
    def __init__(self, *arg, **kw):
        self.__dict__.update(kw)


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
