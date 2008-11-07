from zope.component.testing import PlacelessSetup
import unittest

class TestBFGTestCase(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getTargetClass(self):
        from repoze.bfg.testing import BFGTestCase
        return BFGTestCase

    def _makeOne(self):
        return self._getTargetClass()(methodName='__doc__')

    def test_registerSecurityPolicy_permissive(self):
        case = self._makeOne()
        case.registerSecurityPolicy('user', ('group1', 'group2'),
                                    permissive=True)
        from repoze.bfg.interfaces import ISecurityPolicy
        from zope.component import getUtility
        ut = getUtility(ISecurityPolicy)
        from repoze.bfg.testing import DummyAllowingSecurityPolicy
        self.failUnless(isinstance(ut, DummyAllowingSecurityPolicy))
        self.assertEqual(ut.userid, 'user')
        self.assertEqual(ut.groupids, ('group1', 'group2'))
        
    def test_registerSecurityPolicy_nonpermissive(self):
        case = self._makeOne()
        case.registerSecurityPolicy('user', ('group1', 'group2'),
                                    permissive=False)
        from repoze.bfg.interfaces import ISecurityPolicy
        from zope.component import getUtility
        ut = getUtility(ISecurityPolicy)
        from repoze.bfg.testing import DummyDenyingSecurityPolicy
        self.failUnless(isinstance(ut, DummyDenyingSecurityPolicy))
        self.assertEqual(ut.userid, 'user')
        self.assertEqual(ut.groupids, ('group1', 'group2'))

    def test_registerModels(self):
        ob1 = object()
        ob2 = object()
        models = {'/ob1':ob1, '/ob2':ob2}
        case = self._makeOne()
        case.registerModels(models)
        from zope.component import getAdapter
        from repoze.bfg.interfaces import ITraverserFactory
        adapter = getAdapter(None, ITraverserFactory)
        self.assertEqual(adapter({'PATH_INFO':'/ob1'}), (ob1, '', []))
        self.assertEqual(adapter({'PATH_INFO':'/ob2'}), (ob2, '', []))
        self.assertRaises(KeyError, adapter, {'PATH_INFO':'/ob3'})
        from repoze.bfg.traversal import find_model
        self.assertEqual(find_model(None, '/ob1'), ob1)

    def test_registerTemplate(self):
        case = self._makeOne()
        template = case.registerTemplate('templates/foo')
        from repoze.bfg.testing import DummyTemplateRenderer
        self.failUnless(isinstance(template, DummyTemplateRenderer))
        from repoze.bfg.chameleon_zpt import render_template_to_response
        response = render_template_to_response('templates/foo', foo=1, bar=2)
        self.assertEqual(template.foo, 1)
        self.assertEqual(template.bar, 2)
        self.assertEqual(response.body, '')

    def test_registerEventListener_single(self):
        case = self._makeOne()
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            implements(IEvent)
        L = case.registerEventListener(IEvent)
        from zope.component.event import dispatch
        event = Event()
        dispatch(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        dispatch(object())
        self.assertEqual(len(L), 1)
        
    def test_registerEventListener_defaults(self):
        case = self._makeOne()
        L = case.registerEventListener()
        from zope.component.event import dispatch
        event = object()
        dispatch(event)
        self.assertEqual(len(L), 2)
        self.assertEqual(L[1], event)
        dispatch(object())
        self.assertEqual(len(L), 3)

    def test_registerView_defaults(self):
        case = self._makeOne()
        view = case.registerView('moo.html')
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        from repoze.bfg.view import render_view_to_response
        response = render_view_to_response(None, None, 'moo.html')
        self.assertEqual(view(None, None).body, response.body)
        
    def test_registerView_withresult(self):
        case = self._makeOne()
        view = case.registerView('moo.html', 'yo')
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        from repoze.bfg.view import render_view_to_response
        response = render_view_to_response(None, None, 'moo.html')
        self.assertEqual(response.body, 'yo')

    def test_registerView_custom(self):
        case = self._makeOne()
        def view(context, request):
            from webob import Response
            return Response('123')
        view = case.registerView('moo.html', view=view)
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        from repoze.bfg.view import render_view_to_response
        response = render_view_to_response(None, None, 'moo.html')
        self.assertEqual(response.body, '123')

    def test_registerViewPermission_defaults(self):
        case = self._makeOne()
        view = case.registerViewPermission('moo.html')
        from repoze.bfg.view import view_execution_permitted
        case.registerSecurityPolicy()
        result = view_execution_permitted(None, None, 'moo.html')
        self.failUnless(result)
        self.assertEqual(result.msg, 'message')
        
    def test_registerViewPermission_denying(self):
        case = self._makeOne()
        view = case.registerViewPermission('moo.html', result=False)
        from repoze.bfg.view import view_execution_permitted
        case.registerSecurityPolicy()
        result = view_execution_permitted(None, None, 'moo.html')
        self.failIf(result)
        self.assertEqual(result.msg, 'message')

    def test_registerViewPermission_custom(self):
        class ViewPermission:
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self, secpol):
                return True
                
        case = self._makeOne()
        view = case.registerViewPermission('moo.html',
                                           viewpermission=ViewPermission)
        from repoze.bfg.view import view_execution_permitted
        case.registerSecurityPolicy()
        result = view_execution_permitted(None, None, 'moo.html')
        self.failUnless(result is True)

    def test_registerAdapter(self):
        from zope.interface import implements
        from zope.interface import Interface
        from zope.component import getMultiAdapter
        class provides(Interface):
            pass
        class Provider:
            implements(provides)
            def __init__(self, context, request):
                self.context = context
                self.request = request
        class for_(Interface):
            pass
        class For_:
            implements(for_)
        for1 = For_()
        for2 = For_()
        case = self._makeOne()
        case.registerAdapter(Provider, (for_, for_), provides, name='foo')
        adapter = getMultiAdapter((for1, for2), provides, name='foo')
        self.failUnless(isinstance(adapter, Provider))
        self.assertEqual(adapter.context, for1)
        self.assertEqual(adapter.request, for2)

    def test_registerUtility(self):
        from zope.interface import implements
        from zope.interface import Interface
        from zope.component import getUtility
        class iface(Interface):
            pass
        class impl:
            implements(iface)
            def __call__(self):
                return 'foo'
        case = self._makeOne()
        utility = impl()
        case.registerUtility(utility, iface, name='mudge')
        self.assertEqual(getUtility(iface, name='mudge')(), 'foo')

    def test_makeModel(self):
        case = self._makeOne()
        parent = object()
        model = case.makeModel('name', parent)
        self.assertEqual(model.__name__, 'name')
        self.assertEqual(model.__parent__, parent)

class TestDummyAllowingSecurityPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.testing import DummyAllowingSecurityPolicy
        return DummyAllowingSecurityPolicy

    def _makeOne(self, userid=None, groupids=()):
        klass = self._getTargetClass()
        return klass(userid, groupids)

    def test_authenticated_userid(self):
        policy = self._makeOne('user')
        self.assertEqual(policy.authenticated_userid(None), 'user')
        
    def test_effective_principals_userid(self):
        policy = self._makeOne('user', ('group1',))
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        self.assertEqual(policy.effective_principals(None),
                         [Everyone, Authenticated, 'user', 'group1'])

    def test_effective_principals_nouserid(self):
        policy = self._makeOne()
        from repoze.bfg.security import Everyone
        self.assertEqual(policy.effective_principals(None), [Everyone])

    def test_permits(self):
        policy = self._makeOne()
        self.assertEqual(policy.permits(None, None, None), True)
        
    def test_principals_allowed_by_permission(self):
        policy = self._makeOne('user', ('group1',))
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        self.assertEqual(policy.principals_allowed_by_permission(None, None),
                         [Everyone, Authenticated, 'user', 'group1'])
        

class TestDummyDenyingSecurityPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.testing import DummyDenyingSecurityPolicy
        return DummyDenyingSecurityPolicy

    def _makeOne(self, userid=None, groupids=()):
        klass = self._getTargetClass()
        return klass(userid, groupids)

    def test_authenticated_userid(self):
        policy = self._makeOne('user')
        self.assertEqual(policy.authenticated_userid(None), 'user')
        
    def test_effective_principals_userid(self):
        policy = self._makeOne('user', ('group1',))
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        self.assertEqual(policy.effective_principals(None),
                         [Everyone, Authenticated, 'user', 'group1'])

    def test_effective_principals_nouserid(self):
        policy = self._makeOne()
        from repoze.bfg.security import Everyone
        self.assertEqual(policy.effective_principals(None), [Everyone])

    def test_permits(self):
        policy = self._makeOne()
        self.assertEqual(policy.permits(None, None, None), False)
        
    def test_principals_allowed_by_permission(self):
        policy = self._makeOne('user', ('group1',))
        self.assertEqual(policy.principals_allowed_by_permission(None, None),
                         [])
        
class TestDummyModel(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.testing import DummyModel
        return DummyModel

    def _makeOne(self, name=None, parent=None):
        klass = self._getTargetClass()
        return klass(name, parent)

    def test__setitem__and__getitem__(self):
        class Dummy:
            pass
        dummy = Dummy()
        model = self._makeOne()
        model['abc'] = dummy
        self.assertEqual(dummy.__name__, 'abc')
        self.assertEqual(dummy.__parent__, model)
        self.assertEqual(model['abc'], dummy)
        self.assertRaises(KeyError, model.__getitem__, 'none')

