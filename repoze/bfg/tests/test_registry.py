import unittest
from repoze.bfg.testing import cleanUp

class TestRegistry(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.registry import Registry
        return Registry
    
    def _makeOne(self):
        return self._getTargetClass()()

    def test_registerHandler_and_notify(self):
        registry = self._makeOne()
        self.assertEqual(registry.has_listeners, False)
        from zope.interface import Interface
        from zope.interface import implements
        class IFoo(Interface):
            pass
        class FooEvent(object):
            implements(IFoo)
        L = []
        def f(event):
            L.append(event)
        registry.registerHandler(f, [IFoo])
        self.assertEqual(registry.has_listeners, True)
        event = FooEvent()
        registry.notify(event)
        self.assertEqual(L, [event])

    def test_registerSubscriptionAdapter_and_notify(self):
        registry = self._makeOne()
        self.assertEqual(registry.has_listeners, False)
        from zope.interface import Interface
        class EventHandler:
            pass
        class IFoo(Interface):
            pass
        registry.registerSubscriptionAdapter(EventHandler, [IFoo], Interface)
        self.assertEqual(registry.has_listeners, True)

    def test__override_not_yet_registered(self):
        from repoze.bfg.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        registry = self._makeOne()
        registry._override(package, 'path', opackage, 'oprefix',
                           PackageOverrides=DummyOverrides)
        overrides = registry.queryUtility(IPackageOverrides, name='package')
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def test__override_already_registered(self):
        from repoze.bfg.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        overrides = DummyOverrides(package)
        registry = self._makeOne()
        registry.registerUtility(overrides, IPackageOverrides, name='package')
        registry._override(package, 'path', opackage, 'oprefix',
                           PackageOverrides=DummyOverrides)
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def _registerRenderer(self, reg, name='.txt'):
        from repoze.bfg.interfaces import IRendererFactory
        from repoze.bfg.interfaces import ITemplateRenderer
        from zope.interface import implements
        class Renderer:
            implements(ITemplateRenderer)
            def __init__(self, path):
                pass
            def __call__(self, *arg):
                return 'Hello!'
        reg.registerUtility(Renderer, IRendererFactory, name=name)

    def test_map_view_as_function_context_and_request(self):
        def view(context, request):
            return 'OK'
        reg = self._makeOne()
        result = reg.map_view(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_function_with_attr(self):
        def view(context, request):
            """ """
        reg = self._makeOne()
        result = reg.map_view(view, attr='__name__')
        self.failIf(result is view)
        self.assertRaises(TypeError, result, None, None)

    def test_map_view_as_function_with_attr_and_renderer(self):
        reg = self._makeOne()
        self._registerRenderer(reg)
        def view(context, request):
            """ """
        result = reg.map_view(view, attr='__name__',
                              renderer_name='fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertRaises(TypeError, result, None, None)
        
    def test_map_view_as_function_requestonly(self):
        reg = self._makeOne()
        def view(request):
            return 'OK'
        result = reg.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_function_requestonly_with_attr(self):
        reg = self._makeOne()
        def view(request):
            """ """
        result = reg.map_view(view, attr='__name__')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertRaises(TypeError, result, None, None)

    def test_map_view_as_newstyle_class_context_and_request(self):
        reg = self._makeOne()
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = reg.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_newstyle_class_context_and_request_with_attr(self):
        reg = self._makeOne()
        class view(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return 'OK'
        result = reg.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_newstyle_class_context_and_request_attr_and_renderer(
        self):
        reg = self._makeOne()
        self._registerRenderer(reg)
        class view(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = reg.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')
        
    def test_map_view_as_newstyle_class_requestonly(self):
        reg = self._makeOne()
        class view(object):
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        result = reg.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_newstyle_class_requestonly_with_attr(self):
        reg = self._makeOne()
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return 'OK'
        result = reg.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_newstyle_class_requestonly_with_attr_and_renderer(self):
        reg = self._makeOne()
        self._registerRenderer(reg)
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = reg.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_as_oldstyle_class_context_and_request(self):
        reg = self._makeOne()
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = reg.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_oldstyle_class_context_and_request_with_attr(self):
        reg = self._makeOne()
        class view:
            def __init__(self, context, request):
                pass
            def index(self):
                return 'OK'
        result = reg.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_oldstyle_class_context_and_request_attr_and_renderer(
        self):
        reg = self._makeOne()
        self._registerRenderer(reg)
        class view:
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = reg.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_as_oldstyle_class_requestonly(self):
        reg = self._makeOne()
        class view:
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        result = reg.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_oldstyle_class_requestonly_with_attr(self):
        reg = self._makeOne()
        class view:
            def __init__(self, request):
                pass
            def index(self):
                return 'OK'
        result = reg.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_oldstyle_class_requestonly_attr_and_renderer(self):
        reg = self._makeOne()
        self._registerRenderer(reg)
        class view:
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = reg.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_as_instance_context_and_request(self):
        reg = self._makeOne()
        class View:
            def __call__(self, context, request):
                return 'OK'
        view = View()
        result = reg.map_view(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')
        
    def test_map_view_as_instance_context_and_request_and_attr(self):
        reg = self._makeOne()
        class View:
            def index(self, context, request):
                return 'OK'
        view = View()
        result = reg.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_instance_context_and_request_attr_and_renderer(self):
        reg = self._makeOne()
        self._registerRenderer(reg)
        class View:
            def index(self, context, request):
                return {'a':'1'}
        view = View()
        result = reg.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_as_instance_requestonly(self):
        reg = self._makeOne()
        class View:
            def __call__(self, request):
                return 'OK'
        view = View()
        result = reg.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_instance_requestonly_with_attr(self):
        reg = self._makeOne()
        class View:
            def index(self, request):
                return 'OK'
        view = View()
        result = reg.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_instance_requestonly_with_attr_and_renderer(self):
        reg = self._makeOne()
        self._registerRenderer(reg)
        class View:
            def index(self, request):
                return {'a':'1'}
        view = View()
        result = reg.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_rendereronly(self):
        reg = self._makeOne()
        self._registerRenderer(reg)
        def view(context, request):
            return {'a':'1'}
        result = reg.map_view(
            view,
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_defaultrendereronly(self):
        reg = self._makeOne()
        self._registerRenderer(reg, name='')
        def view(context, request):
            return {'a':'1'}
        result = reg.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

class TestBFGViewGrokker(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.registry import BFGViewGrokker
        return BFGViewGrokker

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_grok_is_bfg_view(self):
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from zope.interface import Interface
        grokker = self._makeOne()
        class obj:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        settings = dict(permission='foo', for_=Interface, name='foo.html',
                        request_type=IRequest, route_name=None,
                        request_method=None, request_param=None,
                        containment=None, attr=None, renderer=None,
                        wrapper=None, xhr=False, header=None,
                        accept=None)
        obj.__bfg_view_settings__ = [settings]
        sm = getSiteManager()
        result = grokker.grok('name', obj, _info='', _registry=sm)
        self.assertEqual(result, True)
        wrapped = sm.adapters.lookup((Interface, IRequest), IView,
                                     name='foo.html')
        self.assertEqual(wrapped(None, None), 'OK')

    def test_grok_is_not_bfg_view(self):
        grokker = self._makeOne()
        class obj:
            pass
        context = DummyContext()
        result = grokker.grok('name', obj, context=context)
        self.assertEqual(result, False)
        actions = context.actions
        self.assertEqual(len(actions), 0)

class TestDefaultRootFactory(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.registry import DefaultRootFactory
        return DefaultRootFactory

    def _makeOne(self, environ):
        return self._getTargetClass()(environ)

    def test_no_matchdict(self):
        environ = {}
        root = self._makeOne(environ)
        self.assertEqual(root.__parent__, None)
        self.assertEqual(root.__name__, None)

    def test_matchdict(self):
        class DummyRequest:
            pass
        request = DummyRequest()
        request.matchdict = {'a':1, 'b':2}
        root = self._makeOne(request)
        self.assertEqual(root.a, 1)
        self.assertEqual(root.b, 2)

class DummyModule:
    __path__ = "foo"
    __name__ = "dummy"
    __file__ = ''


class DummyContext:
    def __init__(self, resolved=DummyModule):
        self.actions = []
        self.info = None
        self.resolved = resolved

class DummyPackage:
    def __init__(self, name):
        self.__name__ = name

class DummyOverrides:
    def __init__(self, package):
        self.package = package
        self.inserted = []

    def insert(self, path, package, prefix):
        self.inserted.append((path, package, prefix))

class DummyRequest:
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        
    def get_response(self, application):
        return application

    def copy(self):
        self.copied = True
        return self

class DummyResponse:
    status = '200 OK'
    headerlist = ()
    def __init__(self, body=None):
        if body is None:
            self.app_iter = ()
        else:
            self.app_iter = [body]
            
