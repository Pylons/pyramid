from repoze.bfg.testing import cleanUp
import unittest

class TestTestingFunctions(unittest.TestCase):
    def setUp(self):
        cleanUp()
        from zope.deprecation import __show__
        __show__.off()

    def tearDown(self):
        cleanUp()
        from zope.deprecation import __show__
        __show__.on()

    def test_registerDummySecurityPolicy(self):
        from repoze.bfg import testing
        testing.registerDummySecurityPolicy('user', ('group1', 'group2'),
                                            permissive=False)
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from zope.component import getUtility
        ut = getUtility(IAuthenticationPolicy)
        from repoze.bfg.testing import DummySecurityPolicy
        self.failUnless(isinstance(ut, DummySecurityPolicy))
        ut = getUtility(IAuthorizationPolicy)
        self.assertEqual(ut.userid, 'user')
        self.assertEqual(ut.groupids, ('group1', 'group2'))
        self.assertEqual(ut.permissive, False)

    def test_registerModels(self):
        ob1 = object()
        ob2 = object()
        models = {'/ob1':ob1, '/ob2':ob2}
        from repoze.bfg import testing
        testing.registerModels(models)
        from zope.component import getAdapter
        from repoze.bfg.interfaces import ITraverserFactory
        adapter = getAdapter(None, ITraverserFactory)
        result = adapter({'PATH_INFO':'/ob1'})
        self.assertEqual(result['context'], ob1)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'ob1',))
        self.assertEqual(result['virtual_root'], ob1)
        self.assertEqual(result['virtual_root_path'], ())
        result = adapter({'PATH_INFO':'/ob2'})
        self.assertEqual(result['context'], ob2)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'ob2',))
        self.assertEqual(result['virtual_root'], ob2)
        self.assertEqual(result['virtual_root_path'], ())
        self.assertRaises(KeyError, adapter, {'PATH_INFO':'/ob3'})
        from repoze.bfg.traversal import find_model
        self.assertEqual(find_model(None, '/ob1'), ob1)

    def test_registerTemplateRenderer(self):
        from repoze.bfg import testing
        renderer = testing.registerTemplateRenderer('templates/foo')
        from repoze.bfg.testing import DummyTemplateRenderer
        self.failUnless(isinstance(renderer, DummyTemplateRenderer))
        from repoze.bfg.chameleon_zpt import render_template_to_response
        response = render_template_to_response('templates/foo', foo=1, bar=2)
        self.assertEqual(dict(foo=1, bar=2), renderer._received)

    def test_registerTemplateRenderer_explicitrenderer(self):
        from repoze.bfg import testing
        def renderer(kw, system):
            raise ValueError
        renderer = testing.registerTemplateRenderer('templates/foo', renderer)
        from repoze.bfg.chameleon_zpt import render_template_to_response
        self.assertRaises(ValueError, render_template_to_response,
                          'templates/foo', foo=1, bar=2)

    def test_registerEventListener_single(self):
        from repoze.bfg import testing
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            implements(IEvent)
        L = testing.registerEventListener(IEvent)
        from zope.component.event import dispatch
        event = Event()
        dispatch(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        dispatch(object())
        self.assertEqual(len(L), 1)

    def test_registerEventListener_multiple(self):
        from repoze.bfg import testing
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            object = 'foo'
            implements(IEvent)
        L = testing.registerEventListener((Interface, IEvent))
        from zope.component.event import objectEventNotify
        event = Event()
        objectEventNotify(event)
        self.assertEqual(len(L), 2)
        self.assertEqual(L[0], 'foo')
        self.assertEqual(L[1], event)
        
    def test_registerEventListener_defaults(self):
        from repoze.bfg import testing
        L = testing.registerEventListener()
        from zope.component.event import dispatch
        event = object()
        dispatch(event)
        self.assertEqual(L[-1], event)
        event2 = object()
        dispatch(event2)
        self.assertEqual(L[-1], event2)

    def test_registerView_defaults(self):
        from repoze.bfg import testing
        view = testing.registerView('moo.html')
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        from repoze.bfg.view import render_view_to_response
        response = render_view_to_response(None, None, 'moo.html')
        self.assertEqual(view(None, None).body, response.body)
        
    def test_registerView_withresult(self):
        from repoze.bfg import testing
        view = testing.registerView('moo.html', 'yo')
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        from repoze.bfg.view import render_view_to_response
        response = render_view_to_response(None, None, 'moo.html')
        self.assertEqual(response.body, 'yo')

    def test_registerView_custom(self):
        from repoze.bfg import testing
        def view(context, request):
            from webob import Response
            return Response('123')
        view = testing.registerView('moo.html', view=view)
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        from repoze.bfg.view import render_view_to_response
        response = render_view_to_response(None, None, 'moo.html')
        self.assertEqual(response.body, '123')

    def test_registerView_with_permission_denying(self):
        from repoze.bfg import testing
        from repoze.bfg.exceptions import Forbidden
        def view(context, request):
            """ """
        view = testing.registerView('moo.html', view=view, permission='bar')
        testing.registerDummySecurityPolicy(permissive=False)
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        from repoze.bfg.view import render_view_to_response
        self.assertRaises(Forbidden, render_view_to_response,
                          None, None, 'moo.html')

    def test_registerView_with_permission_denying2(self):
        from repoze.bfg import testing
        from repoze.bfg.security import view_execution_permitted
        def view(context, request):
            """ """
        view = testing.registerView('moo.html', view=view, permission='bar')
        testing.registerDummySecurityPolicy(permissive=False)
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        result = view_execution_permitted(None, None, 'moo.html')
        self.assertEqual(result, False)

    def test_registerView_with_permission_allowing(self):
        from repoze.bfg import testing
        def view(context, request):
            from webob import Response
            return Response('123')
        view = testing.registerView('moo.html', view=view, permission='bar')
        testing.registerDummySecurityPolicy(permissive=True)
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        from repoze.bfg.view import render_view_to_response
        result = render_view_to_response(None, None, 'moo.html')
        self.assertEqual(result.app_iter, ['123'])

    def test_registerViewPermission_defaults(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg import testing
        view = testing.registerViewPermission('moo.html')
        sm = getSiteManager()
        result = sm.getMultiAdapter(
            (Interface, Interface), IViewPermission, 'moo.html')
        self.assertEqual(result, True)
        
    def test_registerViewPermission_denying(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg import testing
        view = testing.registerViewPermission('moo.html', result=False)
        sm = getSiteManager()
        result = sm.getMultiAdapter(
            (Interface, Interface), IViewPermission, 'moo.html')
        self.assertEqual(result, False)

    def test_registerViewPermission_custom(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IViewPermission
        def viewperm(context, request):
            return True
        from repoze.bfg import testing
        testing.registerViewPermission('moo.html', viewpermission=viewperm)
        sm = getSiteManager()
        result = sm.getMultiAdapter(
            (Interface, Interface), IViewPermission, 'moo.html')
        self.assertEqual(result, True)

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
        from repoze.bfg import testing
        testing.registerAdapter(Provider, (for_, for_), provides, name='foo')
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
        utility = impl()
        from repoze.bfg import testing
        testing.registerUtility(utility, iface, name='mudge')
        self.assertEqual(getUtility(iface, name='mudge')(), 'foo')

    def test_registerRoute(self):
        from repoze.bfg.url import route_url
        from repoze.bfg.interfaces import IRoutesMapper
        from repoze.bfg.testing import registerRoute
        from zope.component import getSiteManager
        class Factory:
            def __init__(self, environ):
                """ """
        class DummyRequest:
            application_url = 'http://example.com'
        registerRoute(':pagename', 'home', Factory)
        sm = getSiteManager()
        mapper = sm.getUtility(IRoutesMapper)
        self.assertEqual(len(mapper.routelist), 1)
        request = DummyRequest()
        self.assertEqual(route_url('home', request, pagename='abc'),
                         'http://example.com/abc')

class TestDummyRootFactory(unittest.TestCase):
    def _makeOne(self, environ):
        from repoze.bfg.testing import DummyRootFactory
        return DummyRootFactory(environ)

    def test_it(self):
        environ = {'bfg.routes.matchdict':{'a':1}}
        factory = self._makeOne(environ)
        self.assertEqual(factory.a, 1)

class TestDummySecurityPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.testing import DummySecurityPolicy
        return DummySecurityPolicy

    def _makeOne(self, userid=None, groupids=(), permissive=True):
        klass = self._getTargetClass()
        return klass(userid, groupids, permissive)

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
        result = policy.principals_allowed_by_permission(None, None)
        self.assertEqual(result, [Everyone, Authenticated, 'user', 'group1'])

    def test_forget(self):
        policy = self._makeOne()
        self.assertEqual(policy.forget(None), [])
        
    def test_remember(self):
        policy = self._makeOne()
        self.assertEqual(policy.remember(None, None), [])
        
        

class TestDummyModel(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.testing import DummyModel
        return DummyModel

    def _makeOne(self, name=None, parent=None, **kw):
        klass = self._getTargetClass()
        return klass(name, parent, **kw)

    def test__setitem__and__getitem__and__delitem__and__contains__and_get(self):
        class Dummy:
            pass
        dummy = Dummy()
        model = self._makeOne()
        model['abc'] = dummy
        self.assertEqual(dummy.__name__, 'abc')
        self.assertEqual(dummy.__parent__, model)
        self.assertEqual(model['abc'], dummy)
        self.assertEqual(model.get('abc'), dummy)
        self.assertRaises(KeyError, model.__getitem__, 'none')
        self.failUnless('abc' in model)
        del model['abc']
        self.failIf('abc' in model)
        self.assertEqual(model.get('abc', 'foo'), 'foo')
        self.assertEqual(model.get('abc'), None)

    def test_extra_params(self):
        model = self._makeOne(foo=1)
        self.assertEqual(model.foo, 1)
        
    def test_clone(self):
        model = self._makeOne('name', 'parent', foo=1, bar=2)
        clone = model.clone('name2', 'parent2', bar=1)
        self.assertEqual(clone.bar, 1)
        self.assertEqual(clone.__name__, 'name2')
        self.assertEqual(clone.__parent__, 'parent2')
        self.assertEqual(clone.foo, 1)

    def test_keys_items_values_len(self):
        class Dummy:
            pass
        model = self._makeOne()
        model['abc'] = Dummy()
        model['def'] = Dummy()
        self.assertEqual(model.values(), model.subs.values())
        self.assertEqual(model.items(), model.subs.items())
        self.assertEqual(model.keys(), model.subs.keys())
        self.assertEqual(len(model), 2)

    def test_nonzero(self):
        model = self._makeOne()
        self.assertEqual(model.__nonzero__(), True)

class TestDummyRequest(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.testing import DummyRequest
        return DummyRequest

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_params(self):
        request = self._makeOne(params = {'say':'Hello'},
                                environ = {'PATH_INFO':'/foo'},
                                headers = {'X-Foo':'YUP'},
                               )
        self.assertEqual(request.params['say'], 'Hello')
        self.assertEqual(request.GET['say'], 'Hello')
        self.assertEqual(request.POST['say'], 'Hello')
        self.assertEqual(request.headers['X-Foo'], 'YUP')
        self.assertEqual(request.environ['PATH_INFO'], '/foo')

    def test_defaults(self):
        request = self._makeOne()
        self.assertEqual(request.method, 'GET')
        self.assertEqual(request.application_url, 'http://example.com')
        self.assertEqual(request.host_url, 'http://example.com')
        self.assertEqual(request.path_url, 'http://example.com')
        self.assertEqual(request.url, 'http://example.com')
        self.assertEqual(request.host, 'example.com:80')
        self.assertEqual(request.content_length, 0)
        self.assertEqual(request.environ.get('PATH_INFO'), None)
        self.assertEqual(request.headers.get('X-Foo'), None)
        self.assertEqual(request.params.get('foo'), None)
        self.assertEqual(request.GET.get('foo'), None)
        self.assertEqual(request.POST.get('foo'), None)
        self.assertEqual(request.cookies.get('type'), None)
        self.assertEqual(request.path, '/')
        self.assertEqual(request.path_info, '/')
        self.assertEqual(request.script_name, '')
        self.assertEqual(request.path_qs, '')
        self.assertEqual(request.view_name, '')
        self.assertEqual(request.subpath, ())
        self.assertEqual(request.context, None)
        self.assertEqual(request.root, None)
        self.assertEqual(request.virtual_root, None)
        self.assertEqual(request.virtual_root_path, ())

    def test_params_explicit(self):
        request = self._makeOne(params = {'foo':'bar'})
        self.assertEqual(request.params['foo'], 'bar')
        self.assertEqual(request.GET['foo'], 'bar')
        self.assertEqual(request.POST['foo'], 'bar')

    def test_environ_explicit(self):
        request = self._makeOne(environ = {'PATH_INFO':'/foo'})
        self.assertEqual(request.environ['PATH_INFO'], '/foo')

    def test_headers_explicit(self):
        request = self._makeOne(headers = {'X-Foo':'YUP'})
        self.assertEqual(request.headers['X-Foo'], 'YUP')

    def test_path_explicit(self):
        request = self._makeOne(path = '/abc')
        self.assertEqual(request.path, '/abc')

    def test_cookies_explicit(self):
        request = self._makeOne(cookies = {'type': 'gingersnap'})
        self.assertEqual(request.cookies['type'], 'gingersnap')

    def test_post_explicit(self):
        POST = {'foo': 'bar', 'baz': 'qux'}
        request = self._makeOne(post=POST)
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.POST, POST)
        # N.B.:  Unlike a normal request, passing 'post' should *not* put
        #        explict POST data into params: doing so masks a possible
        #        XSS bug in the app.  Tests for apps which don't care about
        #        the distinction should just use 'params'.
        self.assertEqual(request.params, {})

    def test_post_empty_shadows_params(self):
        request = self._makeOne(params={'foo': 'bar'}, post={})
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.params.get('foo'), 'bar')
        self.assertEqual(request.POST.get('foo'), None)

    def test_kwargs(self):
        request = self._makeOne(water = 1)
        self.assertEqual(request.water, 1)

class TestDummyTemplateRenderer(unittest.TestCase):
    def _getTargetClass(self, ):
        from repoze.bfg.testing import DummyTemplateRenderer
        return DummyTemplateRenderer

    def _makeOne(self, string_response=''):
        return self._getTargetClass()(string_response=string_response)

    def test_implementation(self):
        renderer = self._makeOne()
        impl = renderer.implementation()
        impl(a=1, b=2)
        self.assertEqual(renderer._received['a'], 1)
        self.assertEqual(renderer._received['b'], 2)

    def test_getattr(self):
        renderer = self._makeOne()
        renderer({'a':1})
        self.assertEqual(renderer.a, 1)
        self.assertRaises(AttributeError, renderer.__getattr__, 'b')

    def test_assert_(self):
        renderer = self._makeOne()
        renderer({'a':1, 'b':2})
        self.assertRaises(AssertionError, renderer.assert_, c=1)
        self.assertRaises(AssertionError, renderer.assert_, b=3)
        self.failUnless(renderer.assert_(a=1, b=2))
        
    def test_nondefault_string_response(self):
        renderer = self._makeOne('abc')
        result = renderer({'a':1, 'b':2})
        self.assertEqual(result, 'abc')

class CleanUpTests(object):
    def setUp(self):
        from repoze.bfg.testing import _cleanups
        self._old_cleanups = _cleanups[:]

    def tearDown(self):
        from repoze.bfg import testing
        testing._cleanups = self._old_cleanups
    
class TestAddCleanUp(CleanUpTests, unittest.TestCase):
    def _getFUT(self, ):
        from repoze.bfg.testing import addCleanUp
        return addCleanUp

    def test_it(self):
        addCleanUp = self._getFUT()
        addCleanUp(1, ('a', 'b'), {'foo':'bar'})
        from repoze.bfg.testing import _cleanups
        self.assertEqual(_cleanups[-1], (1, ('a', 'b'), {'foo':'bar'}))

class TestCleanUp(CleanUpTests, unittest.TestCase):
    def _getFUT(self, ):
        from repoze.bfg.testing import cleanUp
        return cleanUp

    def test_it(self):
        from repoze.bfg.testing import _cleanups
        cleanUp = self._getFUT()
        L = []
        def f(*arg, **kw):
            L.append((arg, kw))
        _cleanups.append((f, ('a', '1'), {'kw':'1'}))
        cleanUp()
        self.assertEqual(L, [(('a', '1'), {'kw':'1'})])
                              
        
