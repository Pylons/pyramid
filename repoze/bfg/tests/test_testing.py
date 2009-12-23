
import unittest

class TestBase(unittest.TestCase):
    def setUp(self):
        from repoze.bfg.threadlocal import manager
        from repoze.bfg.registry import Registry
        manager.clear()
        registry = Registry('testing')
        self.registry = registry
        manager.push({'registry':registry, 'request':None})
        from zope.deprecation import __show__
        __show__.off()

    def tearDown(self):
        from repoze.bfg.threadlocal import manager
        manager.clear()
        from zope.deprecation import __show__
        __show__.on()

class Test_registerDummySecurityPolicy(TestBase):
    def test_registerDummySecurityPolicy(self):
        from repoze.bfg import testing
        testing.registerDummySecurityPolicy('user', ('group1', 'group2'),
                                            permissive=False)
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        ut = self.registry.getUtility(IAuthenticationPolicy)
        from repoze.bfg.testing import DummySecurityPolicy
        self.failUnless(isinstance(ut, DummySecurityPolicy))
        ut = self.registry.getUtility(IAuthorizationPolicy)
        self.assertEqual(ut.userid, 'user')
        self.assertEqual(ut.groupids, ('group1', 'group2'))
        self.assertEqual(ut.permissive, False)

class Test_registerModels(TestBase):
    def test_registerModels(self):
        ob1 = object()
        ob2 = object()
        models = {'/ob1':ob1, '/ob2':ob2}
        from repoze.bfg import testing
        testing.registerModels(models)
        from repoze.bfg.interfaces import ITraverser
        adapter = self.registry.getAdapter(None, ITraverser)
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

class Test_registerTemplateRenderer(TestBase):
    def test_registerTemplateRenderer(self):
        from repoze.bfg import testing
        renderer = testing.registerTemplateRenderer('templates/foo')
        from repoze.bfg.testing import DummyTemplateRenderer
        self.failUnless(isinstance(renderer, DummyTemplateRenderer))
        from repoze.bfg.chameleon_zpt import render_template_to_response
        render_template_to_response('templates/foo', foo=1, bar=2)
        self.assertEqual(dict(foo=1, bar=2), renderer._received)

    def test_registerTemplateRenderer_explicitrenderer(self):
        from repoze.bfg import testing
        def renderer(kw, system):
            raise ValueError
        renderer = testing.registerTemplateRenderer('templates/foo', renderer)
        from repoze.bfg.chameleon_zpt import render_template_to_response
        self.assertRaises(ValueError, render_template_to_response,
                          'templates/foo', foo=1, bar=2)

class Test_registerEventListener(TestBase):
    def test_registerEventListener_single(self):
        from repoze.bfg import testing
        L = testing.registerEventListener(IDummy)
        event = DummyEvent()
        self.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        self.registry.notify(object())
        self.assertEqual(len(L), 1)

    def test_registerEventListener_multiple(self):
        from repoze.bfg import testing
        L = testing.registerEventListener((Interface, IDummy))
        event = DummyEvent()
        event.object = 'foo'
        # the below is the equivalent of z.c.event.objectEventNotify(event)
        self.registry.subscribers((event.object, event), None)
        self.assertEqual(len(L), 2)
        self.assertEqual(L[0], 'foo')
        self.assertEqual(L[1], event)
        
    def test_registerEventListener_defaults(self):
        from repoze.bfg import testing
        L = testing.registerEventListener()
        event = object()
        self.registry.notify(event)
        self.assertEqual(L[-1], event)
        event2 = object()
        self.registry.notify(event2)
        self.assertEqual(L[-1], event2)

class Test_registerView(TestBase):
    def test_registerView_defaults(self):
        from repoze.bfg import testing
        view = testing.registerView('moo.html')
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        from repoze.bfg.view import render_view_to_response
        request = DummyRequest()
        request.registry = self.registry
        response = render_view_to_response(None, request, 'moo.html')
        self.assertEqual(view(None, None).body, response.body)
        
    def test_registerView_withresult(self):
        from repoze.bfg import testing
        view = testing.registerView('moo.html', 'yo')
        import types
        self.failUnless(isinstance(view, types.FunctionType))
        from repoze.bfg.view import render_view_to_response
        request = DummyRequest()
        request.registry = self.registry
        response = render_view_to_response(None, request, 'moo.html')
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
        request = DummyRequest()
        request.registry = self.registry
        response = render_view_to_response(None, request, 'moo.html')
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
        request = DummyRequest()
        request.registry = self.registry
        self.assertRaises(Forbidden, render_view_to_response,
                          None, request, 'moo.html')

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
        request = DummyRequest()
        request.registry = self.registry
        result = render_view_to_response(None, request, 'moo.html')
        self.assertEqual(result.app_iter, ['123'])

    def test_registerViewPermission_defaults(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg import testing
        testing.registerViewPermission('moo.html')
        result = self.registry.getMultiAdapter(
            (Interface, Interface), IViewPermission, 'moo.html')
        self.assertEqual(result, True)
        
    def test_registerViewPermission_denying(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg import testing
        testing.registerViewPermission('moo.html', result=False)
        result = self.registry.getMultiAdapter(
            (Interface, Interface), IViewPermission, 'moo.html')
        self.assertEqual(result, False)

    def test_registerViewPermission_custom(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IViewPermission
        def viewperm(context, request):
            return True
        from repoze.bfg import testing
        testing.registerViewPermission('moo.html', viewpermission=viewperm)
        result = self.registry.getMultiAdapter(
            (Interface, Interface), IViewPermission, 'moo.html')
        self.assertEqual(result, True)

class Test_registerAdapter(TestBase):
    def test_registerAdapter(self):
        from zope.interface import Interface
        class provides(Interface):
            pass
        class Provider:
            pass
        class for_(Interface):
            pass
        from repoze.bfg import testing
        testing.registerAdapter(Provider, (for_, for_), provides, name='foo')
        adapter = self.registry.adapters.lookup(
            (for_, for_), provides, name='foo')
        self.assertEqual(adapter, Provider)

    def test_registerAdapter_notlist(self):
        from zope.interface import Interface
        class provides(Interface):
            pass
        class Provider:
            pass
        class for_(Interface):
            pass
        from repoze.bfg import testing
        testing.registerAdapter(Provider, for_, provides, name='foo')
        adapter = self.registry.adapters.lookup(
            (for_,), provides, name='foo')
        self.assertEqual(adapter, Provider)

class Test_registerUtility(TestBase):
    def test_registerUtility(self):
        from zope.interface import implements
        from zope.interface import Interface
        class iface(Interface):
            pass
        class impl:
            implements(iface)
            def __call__(self):
                return 'foo'
        utility = impl()
        from repoze.bfg import testing
        testing.registerUtility(utility, iface, name='mudge')
        self.assertEqual(self.registry.getUtility(iface, name='mudge')(), 'foo')

class Test_registerSubscriber(TestBase):
    def test_it(self):
        from repoze.bfg import testing
        L = []
        def subscriber(event):
            L.append(event)
        testing.registerSubscriber(subscriber, iface=IDummy)
        event = DummyEvent()
        self.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        self.registry.notify(object())
        self.assertEqual(len(L), 1)

class Test_registerRoute(TestBase):
    def test_registerRoute(self):
        from repoze.bfg.url import route_url
        from repoze.bfg.interfaces import IRoutesMapper
        from repoze.bfg.testing import registerRoute
        registerRoute(':pagename', 'home', DummyFactory)
        mapper = self.registry.getUtility(IRoutesMapper)
        self.assertEqual(len(mapper.routelist), 1)
        request = DummyRequest()
        self.assertEqual(route_url('home', request, pagename='abc'),
                         'http://example.com/abc')

class Test_registerRoutesMapper(TestBase):
    def test_registerRoutesMapper(self):
        from repoze.bfg.interfaces import IRoutesMapper
        from repoze.bfg.testing import registerRoutesMapper
        result = registerRoutesMapper()
        mapper = self.registry.getUtility(IRoutesMapper)
        self.assertEqual(result, mapper)

class Test_registerSettings(TestBase):
    def test_registerSettings(self):
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.testing import registerSettings
        registerSettings({'a':1, 'b':2})
        settings = self.registry.getUtility(ISettings)
        self.assertEqual(settings['a'], 1)
        self.assertEqual(settings['b'], 2)
        registerSettings(b=3, c=4)
        settings = self.registry.getUtility(ISettings)
        self.assertEqual(settings['a'], 1)
        self.assertEqual(settings['b'], 3)
        self.assertEqual(settings['c'], 4)

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

    def test_ctor_with__provides__(self):
        model = self._makeOne(__provides__=IDummy)
        self.failUnless(IDummy.providedBy(model))

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
        from repoze.bfg.threadlocal import get_current_registry
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
        self.assertEqual(request.registry, get_current_registry())

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

class Test_setUp(unittest.TestCase):
    def _callFUT(self, **kw):
        from repoze.bfg.testing import setUp
        return setUp(**kw)

    def test_it_defaults(self):
        from repoze.bfg.threadlocal import manager
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.registry import Registry
        from zope.component import getSiteManager
        old = True
        manager.push(old)
        try:
            config = self._callFUT()
            current = manager.get()
            self.failIf(current is old)
            self.assertEqual(config.registry, current['registry'])
            self.assertEqual(current['registry'].__class__, Registry)
            self.assertEqual(current['request'], None)
        finally:
            result = getSiteManager.sethook(None)
            self.assertEqual(result, get_current_registry)
            getSiteManager.reset()
            manager.clear()

    def test_it_with_registry(self):
        from zope.component import getSiteManager
        from repoze.bfg.threadlocal import manager
        registry = object()
        try:
            self._callFUT(registry=registry)
            current = manager.get()
            self.assertEqual(current['registry'], registry)
        finally:
            getSiteManager.reset()
            manager.clear()
            
    def test_it_with_request(self):
        from zope.component import getSiteManager
        from repoze.bfg.threadlocal import manager
        request = object()
        try:
            self._callFUT(request=request)
            current = manager.get()
            self.assertEqual(current['request'], request)
        finally:
            getSiteManager.reset()
            manager.clear()

    def test_it_with_hook_zca_false(self):
        from zope.component import getSiteManager
        from repoze.bfg.threadlocal import manager
        registry = object()
        try:
            self._callFUT(registry=registry, hook_zca=False)
            sm = getSiteManager()
            self.failIf(sm is registry)
        finally:
            getSiteManager.reset()
            manager.clear()

class Test_cleanUp(Test_setUp):
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.testing import cleanUp
        return cleanUp(*arg, **kw)
        
class Test_tearDown(unittest.TestCase):
    def _callFUT(self, **kw):
        from repoze.bfg.testing import tearDown
        return tearDown(**kw)

    def test_defaults(self):
        from repoze.bfg.threadlocal import manager
        from zope.component import getSiteManager
        registry = DummyRegistry()
        old = {'registry':registry}
        hook = lambda *arg: None
        try:
            getSiteManager.sethook(hook)
            manager.push(old)
            self._callFUT()
            current = manager.get()
            self.assertNotEqual(current, old)
            self.assertEqual(registry.inited, 2)
        finally:
            result = getSiteManager.sethook(None)
            self.assertNotEqual(result, hook)
            getSiteManager.reset()
            manager.clear()

    def test_registry_cannot_be_inited(self):
        from repoze.bfg.threadlocal import manager
        registry = DummyRegistry()
        def raiseit(name):
            raise TypeError
        registry.__init__ = raiseit
        old = {'registry':registry}
        try:
            manager.push(old)
            self._callFUT() # doesn't blow up
            current = manager.get()
            self.assertNotEqual(current, old)
            self.assertEqual(registry.inited, 1)
        finally:
            manager.clear()

    def test_unhook_zc_false(self):
        from repoze.bfg.threadlocal import manager
        from zope.component import getSiteManager
        hook = lambda *arg: None
        try:
            getSiteManager.sethook(hook)
            self._callFUT(unhook_zca=False)
        finally:
            result = getSiteManager.sethook(None)
            self.assertEqual(result, hook)
            getSiteManager.reset()
            manager.clear()

from zope.interface import Interface
from zope.interface import implements
        
class IDummy(Interface):
    pass

class DummyEvent:
    implements(IDummy)

class DummyRequest:
    application_url = 'http://example.com'

class DummyFactory:
    def __init__(self, environ):
        """ """

class DummyRegistry(object):
    inited = 0
    __name__ = 'name'
    def __init__(self, name=''):
        self.inited = self.inited + 1
        
