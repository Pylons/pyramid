import unittest

class TestRepozeWho1AuthenticationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.authentication import RepozeWho1AuthenticationPolicy
        return RepozeWho1AuthenticationPolicy

    def _makeOne(self):
        return self._getTargetClass()()
    
    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne())

    def test_authenticated_userid_None(self):
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(context, request), None)
        
    def test_authenticated_userid(self):
        context = DummyContext()
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(context, request), 'fred')

    def test_effective_principals_None(self):
        from repoze.bfg.security import Everyone
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone])

    def test_effective_principals_userid_only(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        context = DummyContext()
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred'}})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone, Authenticated, 'fred'])

    def test_effective_principals_userid_and_groups(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        context = DummyContext()
        request = DummyRequest(
            {'repoze.who.identity':{'repoze.who.userid':'fred',
                                    'groups':['quux', 'biz']}})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone, Authenticated, 'fred', 'quux', 'biz'])

    def test_remember_no_plugins(self):
        context = DummyContext()
        authtkt = DummyPlugin()
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.remember(context, request, 'fred')
        self.assertEqual(result, [])

    def test_remember(self):
        context = DummyContext()
        authtkt = DummyPlugin()
        request = DummyRequest(
            {'repoze.who.plugins':{'auth_tkt':authtkt}})
        policy = self._makeOne()
        result = policy.remember(context, request, 'fred')
        self.assertEqual(result[0], request.environ)
        self.assertEqual(result[1], {'repoze.who.userid':'fred'})
        
    def test_forget_no_plugins(self):
        context = DummyContext()
        authtkt = DummyPlugin()
        request = DummyRequest({})
        policy = self._makeOne()
        result = policy.forget(context, request)
        self.assertEqual(result, [])

    def test_forget(self):
        context = DummyContext()
        authtkt = DummyPlugin()
        request = DummyRequest(
            {'repoze.who.plugins':{'auth_tkt':authtkt},
             'repoze.who.identity':{'repoze.who.userid':'fred'},
             })
        policy = self._makeOne()
        result = policy.forget(context, request)
        self.assertEqual(result[0], request.environ)
        self.assertEqual(result[1], request.environ['repoze.who.identity'])

class TestRemoteUserAuthenticationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.authentication import RemoteUserAuthenticationPolicy
        return RemoteUserAuthenticationPolicy

    def _makeOne(self):
        return self._getTargetClass()()
    
    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne())

    def test_authenticated_userid_None(self):
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(context, request), None)
        
    def test_authenticated_userid(self):
        context = DummyContext()
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(context, request), 'fred')

    def test_effective_principals_None(self):
        from repoze.bfg.security import Everyone
        context = DummyContext()
        request = DummyRequest({})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone])

    def test_effective_principals(self):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        context = DummyContext()
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(context, request),
                         [Everyone, Authenticated, 'fred'])

    def test_remember(self):
        context = DummyContext()
        authtkt = DummyPlugin()
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        result = policy.remember(context, request, 'fred')
        self.assertEqual(result, [])
        
    def test_forget(self):
        context = DummyContext()
        authtkt = DummyPlugin()
        request = DummyRequest({'REMOTE_USER':'fred'})
        policy = self._makeOne()
        result = policy.forget(context, request)
        self.assertEqual(result, [])

class DummyContext:
    pass

class DummyRequest:
    def __init__(self, environ):
        self.environ = environ

class DummyPlugin:
    def remember(self, environ, identity):
        return environ, identity
    
    def forget(self, environ, identity):
        return environ, identity
