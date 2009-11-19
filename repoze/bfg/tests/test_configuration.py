import unittest

from repoze.bfg.testing import cleanUp

class ConfiguratorTests(unittest.TestCase):
    def _makeOne(self, registry=None):
        from repoze.bfg.registry import Registry
        from repoze.bfg.configuration import Configurator
        if registry is None:
            registry = Registry()
        return Configurator(registry)

    def _registerRenderer(self, config, name='.txt'):
        from repoze.bfg.interfaces import IRendererFactory
        from repoze.bfg.interfaces import ITemplateRenderer
        from zope.interface import implements
        class Renderer:
            implements(ITemplateRenderer)
            def __init__(self, path):
                self.__class__.path = path
            def __call__(self, *arg):
                return 'Hello!'
        config.reg.registerUtility(Renderer, IRendererFactory, name=name)
        return Renderer

    def _getViewCallable(self, config, ctx_iface=None, request_iface=None,
                         name=''):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        if ctx_iface is None:
            ctx_iface = Interface
        if request_iface is None:
            request_iface = IRequest
        return config.reg.adapters.lookup(
            (ctx_iface, request_iface), IView, name=name,
            default=None)

    def _callDefaultConfiguration(self, *arg, **kw):
        inst = self._makeOne()
        inst.default_configuration(*arg, **kw)
        return inst.reg

    def _getRouteRequestIface(self, config, name):
        from repoze.bfg.interfaces import IRouteRequest
        iface = config.reg.getUtility(IRouteRequest, name)
        return iface

    def _assertNotFound(self, wrapper, *arg):
        from repoze.bfg.exceptions import NotFound
        self.assertRaises(NotFound, wrapper, *arg)

    def test_view_view_callable_None_no_renderer(self):
        from zope.configuration.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.view)

    def test_view_with_request_type_and_route_name(self):
        from zope.configuration.exceptions import ConfigurationError
        config = self._makeOne()
        view = lambda *arg: 'OK'
        self.assertRaises(ConfigurationError, config.view, view, '', None,
                          None, True, True)

    def test_view_view_callable_None_with_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config, name='dummy')
        config.view(renderer='dummy')
        view = self._getViewCallable(config)
        self.failUnless('Hello!' in view(None, None).body)

    def test_wrapped_view_is_decorated(self):
        def view(request): # request-only wrapper
            """ """
        config = self._makeOne()
        config.view(view=view)
        wrapper = self._getViewCallable(config)
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)

    def test_view_with_function_callable(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_view_with_function_callable_requestonly(self):
        def view(request):
            return 'OK'
        config = self._makeOne()
        config.view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_view_as_instance(self):
        class AView:
            def __call__(self, context, request):
                """ """
                return 'OK'
        view = AView()
        config = self._makeOne()
        config.view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_view_as_instance_requestonly(self):
        class AView:
            def __call__(self, request):
                """ """
                return 'OK'
        view = AView()
        config = self._makeOne()
        config.view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_view_as_oldstyle_class(self):
        class view:
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self):
                return 'OK'
        config = self._makeOne()
        config.view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_view_as_oldstyle_class_requestonly(self):
        class view:
            def __init__(self, request):
                self.request = request

            def __call__(self):
                return 'OK'
        config = self._makeOne()
        config.view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_view_for_as_class(self):
        from zope.interface import implementedBy
        view = lambda *arg: 'OK'
        class Foo:
            pass
        config = self._makeOne()
        config.view(for_=Foo, view=view)
        foo = implementedBy(Foo)
        wrapper = self._getViewCallable(config, foo)
        self.assertEqual(wrapper, view)

    def test_view_for_as_iface(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(for_=IDummy, view=view)
        wrapper = self._getViewCallable(config, IDummy)
        self.assertEqual(wrapper, view)

    def test_view_register_secured_view(self):
        from zope.component import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import ISecuredView
        view = lambda *arg: 'OK'
        view.__call_permissive__ = view
        config = self._makeOne()
        config.view(view=view)
        wrapper = config.reg.adapters.lookup(
            (Interface, IRequest), ISecuredView, name='', default=None)
        self.assertEqual(wrapper, view)

    def test_view_multiview_replaces_existing_view(self):
        from zope.component import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IMultiView
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.reg.registerAdapter(view, (Interface, IRequest), IView, name='')
        config.view(view=view)
        wrapper = self._getViewCallable(config)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')

    def test_view_multiview_replaces_multiview(self):
        from zope.component import Interface
        from zope.interface import implements
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IMultiView
        class DummyMultiView:
            implements(IMultiView)
            def __init__(self):
                self.views = []
                self.name = 'name'
            def add(self, view, score):
                self.views.append(view)
            def __call__(self, context, request):
                return 'OK1'
            def __permitted__(self, context, request):
                """ """
        view = DummyMultiView()
        config = self._makeOne()
        config.reg.registerAdapter(view, (Interface, IRequest),
                                   IMultiView, name='')
        view2 = lambda *arg: 'OK2'
        config.view(view=view2)
        wrapper = self._getViewCallable(config)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper.views, [view2])
        self.assertEqual(wrapper(None, None), 'OK1')

    def test_view_multiview_call_ordering(self):
        from zope.interface import directlyProvides
        def view1(context, request): return 'view1'
        def view2(context, request): return 'view2'
        def view3(context, request): return 'view3'
        def view4(context, request): return 'view4'
        def view5(context, request): return 'view5'
        def view6(context, request): return 'view6'
        def view7(context, request): return 'view7'
        def view8(context, request): return 'view8'
        config = self._makeOne()
        config.view(view=view1)
        config.view(view=view2, request_method='POST')
        config.view(view=view3,request_param='param')
        config.view(view=view4, containment=IDummy)
        config.view(view=view5, request_method='POST', request_param='param')
        config.view(view=view6, request_method='POST', containment=IDummy)
        config.view(view=view7, request_param='param', containment=IDummy)
        config.view(view=view8, request_method='POST', request_param='param',
                    containment=IDummy)

        wrapper = self._getViewCallable(config)

        ctx = DummyContext()
        request = DummyRequest()
        request.method = 'GET'
        request.params = {}
        self.assertEqual(wrapper(ctx, request), 'view1')

        ctx = DummyContext()
        request = DummyRequest()
        request.params = {}
        request.method = 'POST'
        self.assertEqual(wrapper(ctx, request), 'view2')

        ctx = DummyContext()
        request = DummyRequest()
        request.params = {'param':'1'}
        request.method = 'GET'
        self.assertEqual(wrapper(ctx, request), 'view3')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = DummyRequest()
        request.method = 'GET'
        request.params = {}
        self.assertEqual(wrapper(ctx, request), 'view4')

        ctx = DummyContext()
        request = DummyRequest()
        request.method = 'POST'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view5')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = DummyRequest()
        request.params = {}
        request.method = 'POST'
        self.assertEqual(wrapper(ctx, request), 'view6')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = DummyRequest()
        request.method = 'GET'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view7')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = DummyRequest()
        request.method = 'POST'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view8')

    def test_view_with_relative_template_renderer(self):
        class view(object):
            def __init__(self, context, request):
                self.request = request
                self.context = context

            def __call__(self):
                return {'a':'1'}
        config = self._makeOne()
        renderer = self._registerRenderer(config)
        fixture = 'fixtures/minimal.txt'
        config.view(view=view, renderer=fixture)
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        result = wrapper(None, request)
        self.assertEqual(result.body, 'Hello!')
        self.assertEqual(renderer.path, 'fixtures/minimal.txt')

    def test_view_with_relative_template_renderer_no_callable(self):
        config = self._makeOne()
        renderer = self._registerRenderer(config)
        fixture = 'fixtures/minimal.txt'
        config.view(view=None, renderer=fixture)
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        result = wrapper(None, request)
        self.assertEqual(result.body, 'Hello!')
        self.assertEqual(renderer.path, 'fixtures/minimal.txt')

    def test_view_with_request_type_as_iface(self):
        def view(context, request):
            return 'OK'
        config = self._makeOne()
        config.view(request_type=IDummy, view=view)
        wrapper = self._getViewCallable(config, None, IDummy)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_view_with_request_type_as_noniface(self):
        from zope.interface import providedBy
        def view(context, request):
            return 'OK'
        config = self._makeOne()
        config.view(request_type=object, view=view)
        request_iface = providedBy(object)
        wrapper = self._getViewCallable(config, None, request_iface)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_view_with_route_name(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, route_name='foo')
        request_type = self._getRouteRequestIface(config, 'foo')
        wrapper = self._getViewCallable(config, None, request_type)
        self.assertEqual(wrapper(None, None), 'OK')

    def test_view_with_request_method_true(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, request_method='POST')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.method = 'POST'
        self.assertEqual(wrapper(None, request), 'OK')

    def test_view_with_request_method_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, request_method='POST')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.method = 'GET'
        self._assertNotFound(wrapper, None, request)

    def test_view_with_request_param_noval_true(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, request_param='abc')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.params = {'abc':''}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_view_with_request_param_noval_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, request_param='abc')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.params = {}
        self._assertNotFound(wrapper, None, request)

    def test_view_with_request_param_val_true(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, request_param='abc=123')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.params = {'abc':'123'}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_view_with_request_param_val_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, request_param='abc=123')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.params = {'abc':''}
        self._assertNotFound(wrapper, None, request)

    def test_view_with_xhr_true(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, xhr=True)
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_view_with_xhr_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, xhr=True)
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.is_xhr = False
        self._assertNotFound(wrapper, None, request)

    def test_view_with_header_badregex(self):
        from zope.configuration.exceptions import ConfigurationError
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self.assertRaises(ConfigurationError,
                          config.view, view=view, header='Host:a\\')

    def test_view_with_header_noval_match(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, header='Host')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.headers = {'Host':'whatever'}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_view_with_header_noval_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, header='Host')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.headers = {'NotHost':'whatever'}
        self._assertNotFound(wrapper, None, request)

    def test_view_with_header_val_match(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, header=r'Host:\d')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.headers = {'Host':'1'}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_view_with_header_val_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, header=r'Host:\d')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.headers = {'Host':'abc'}
        self._assertNotFound(wrapper, None, request)

    def test_view_with_accept_match(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, accept='text/xml')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.accept = ['text/xml']
        self.assertEqual(wrapper(None, request), 'OK')

    def test_view_with_accept_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, accept='text/xml')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.accept = ['text/html']
        self._assertNotFound(wrapper, None, request)

    def test_view_with_containment_true(self):
        from zope.interface import directlyProvides
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, containment=IDummy)
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        context = DummyContext()
        directlyProvides(context, IDummy)
        self.assertEqual(wrapper(context, None), 'OK')

    def test_view_with_containment_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, containment=IDummy)
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        context = DummyContext()
        self._assertNotFound(wrapper, context, None)

    def test_view_with_path_info_badregex(self):
        from zope.configuration.exceptions import ConfigurationError
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self.assertRaises(ConfigurationError,
                          config.view, view=view, path_info='\\')

    def test_with_path_info_match(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, path_info='/foo')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.path_info = '/foo'
        self.assertEqual(wrapper(None, request), 'OK')

    def test_with_path_info_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.view(view=view, path_info='/foo')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.path_info = '/'
        self._assertNotFound(wrapper, None, request)

    def _assertRoute(self, config, name, path, num_predicates=0):
        from repoze.bfg.interfaces import IRoutesMapper
        mapper = config.reg.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, name)
        self.assertEqual(route.path, path)
        self.assertEqual(len(routes[0].predicates), num_predicates)
        return route

    def test_route_defaults(self):
        config = self._makeOne()
        config.route('name', 'path')
        self._assertRoute(config, 'name', 'path')

    def test_route_with_xhr(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', xhr=True)
        request_type = self._getRouteRequestIface(config, 'name')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(predicate(None, request), True)
        request = DummyRequest()
        request.is_xhr = False
        self.assertEqual(predicate(None, request), False)

    def test_route_with_request_method(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', request_method='GET')
        request_type = self._getRouteRequestIface(config, 'name')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = DummyRequest()
        request.method = 'GET'
        self.assertEqual(predicate(None, request), True)
        request = DummyRequest()
        request.method = 'POST'
        self.assertEqual(predicate(None, request), False)

    def test_route_with_path_info(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', path_info='/foo')
        request_type = self._getRouteRequestIface(config, 'name')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = DummyRequest()
        request.path_info = '/foo'
        self.assertEqual(predicate(None, request), True)
        request = DummyRequest()
        request.path_info = '/'
        self.assertEqual(predicate(None, request), False)

    def test_route_with_request_param(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', request_param='abc')
        request_type = self._getRouteRequestIface(config, 'name')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = DummyRequest()
        request.params = {'abc':'123'}
        self.assertEqual(predicate(None, request), True)
        request = DummyRequest()
        request.params = {}
        self.assertEqual(predicate(None, request), False)

    def test_route_with_header(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', header='Host')
        request_type = self._getRouteRequestIface(config, 'name')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = DummyRequest()
        request.headers = {'Host':'example.com'}
        self.assertEqual(predicate(None, request), True)
        request = DummyRequest()
        request.headers = {}
        self.assertEqual(predicate(None, request), False)

    def test_route_with_accept(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', accept='text/xml')
        request_type = self._getRouteRequestIface(config, 'name')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = DummyRequest()
        request.accept = ['text/xml']
        self.assertEqual(predicate(None, request), True)
        request = DummyRequest()
        request.accept = ['text/html']
        self.assertEqual(predicate(None, request), False)

    def test_route_with_view(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')

    def test_route_with_view_for(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view, view_for=IDummy)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, IDummy, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')
        wrapper = self._getViewCallable(config, IOther, request_type)
        self.assertEqual(wrapper, None)

    def test_route_with_view_for_alias(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view, for_=IDummy)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, IDummy, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')
        wrapper = self._getViewCallable(config, IOther, request_type)
        self.assertEqual(wrapper, None)

    def test_route_with_view_request_method(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view, view_request_method='GET')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        route = self._assertRoute(config, 'name', 'path')
        request = DummyRequest()
        request.method = 'GET'
        self.assertEqual(wrapper(None, request), 'OK')
        request = DummyRequest()
        request.method = 'POST'
        self._assertNotFound(wrapper, None, request)

    def test_route_with_view_header(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view, view_header='Host')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        route = self._assertRoute(config, 'name', 'path')
        request = DummyRequest()
        request.headers = {'Host':'abc'}
        self.assertEqual(wrapper(None, request), 'OK')
        request = DummyRequest()
        request.headers = {}
        self._assertNotFound(wrapper, None, request)

    def test_route_with_view_xhr(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view, view_xhr=True)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        route = self._assertRoute(config, 'name', 'path')
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')
        request = DummyRequest()
        request.is_xhr = False
        self._assertNotFound(wrapper, None, request)

    def test_route_with_view_path_info(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view, view_path_info='/foo')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        route = self._assertRoute(config, 'name', 'path')
        request = DummyRequest()
        request.path_info = '/foo'
        self.assertEqual(wrapper(None, request), 'OK')
        request = DummyRequest()
        request.path_info = '/'
        self._assertNotFound(wrapper, None, request)

    def test_route_with_view_accept(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view, view_accept='text/xml')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        route = self._assertRoute(config, 'name', 'path')
        request = DummyRequest()
        request.accept = ['text/xml']
        self.assertEqual(wrapper(None, request), 'OK')
        request = DummyRequest()
        request.accept = ['text/html']
        self._assertNotFound(wrapper, None, request)

    def test_route_with_view_containment(self):
        from zope.interface import directlyProvides
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view, view_containment=IDummy)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        route = self._assertRoute(config, 'name', 'path')
        context = DummyContext()
        directlyProvides(context, IDummy)
        self.assertEqual(wrapper(context, None), 'OK')
        self._assertNotFound(wrapper, None, None)

    def test_route_with_view_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config)
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view,
                     view_renderer='fixtures/minimal.txt')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        route = self._assertRoute(config, 'name', 'path')
        self.assertEqual(wrapper(None, None).body, 'Hello!')

    def test_route_with_view_renderer_alias(self):
        config = self._makeOne()
        self._registerRenderer(config)
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view,
                     renderer='fixtures/minimal.txt')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        route = self._assertRoute(config, 'name', 'path')
        self.assertEqual(wrapper(None, None).body, 'Hello!')

    def test_route_with_view_permission(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        config = self._makeOne()
        policy = lambda *arg: None
        config.reg.registerUtility(policy, IAuthenticationPolicy)
        config.reg.registerUtility(policy, IAuthorizationPolicy)
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view, view_permission='edit')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        route = self._assertRoute(config, 'name', 'path')
        self.failUnless(hasattr(wrapper, '__call_permissive__'))

    def test_route_with_view_permission_alias(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        config = self._makeOne()
        policy = lambda *arg: None
        config.reg.registerUtility(policy, IAuthenticationPolicy)
        config.reg.registerUtility(policy, IAuthorizationPolicy)
        view = lambda *arg: 'OK'
        config.route('name', 'path', view=view, permission='edit')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        route = self._assertRoute(config, 'name', 'path')
        self.failUnless(hasattr(wrapper, '__call_permissive__'))

    def test__override_not_yet_registered(self):
        from repoze.bfg.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        config = self._makeOne()
        config._override(package, 'path', opackage, 'oprefix',
                         PackageOverrides=DummyOverrides)
        overrides = config.reg.queryUtility(IPackageOverrides,
                                            name='package')
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def test__override_already_registered(self):
        from repoze.bfg.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        overrides = DummyOverrides(package)
        config = self._makeOne()
        config.reg.registerUtility(overrides, IPackageOverrides,
                                   name='package')
        config._override(package, 'path', opackage, 'oprefix',
                         PackageOverrides=DummyOverrides)
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def test__map_view_as_function_context_and_request(self):
        def view(context, request):
            return 'OK'
        config = self._makeOne()
        result = config._map_view(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_function_with_attr(self):
        def view(context, request):
            """ """
        config = self._makeOne()
        result = config._map_view(view, attr='__name__')
        self.failIf(result is view)
        self.assertRaises(TypeError, result, None, None)

    def test__map_view_as_function_with_attr_and_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config)
        view = lambda *arg: 'OK'
        result = config._map_view(view, attr='__name__',
                                 renderer_name='fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertRaises(TypeError, result, None, None)
        
    def test__map_view_as_function_requestonly(self):
        config = self._makeOne()
        def view(request):
            return 'OK'
        result = config._map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_function_requestonly_with_attr(self):
        config = self._makeOne()
        def view(request):
            """ """
        result = config._map_view(view, attr='__name__')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertRaises(TypeError, result, None, None)

    def test__map_view_as_newstyle_class_context_and_request(self):
        config = self._makeOne()
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = config._map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_newstyle_class_context_and_request_with_attr(self):
        config = self._makeOne()
        class view(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return 'OK'
        result = config._map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_newstyle_class_context_and_request_attr_and_renderer(
        self):
        config = self._makeOne()
        self._registerRenderer(config)
        class view(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = config._map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')
        
    def test__map_view_as_newstyle_class_requestonly(self):
        config = self._makeOne()
        class view(object):
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        result = config._map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_newstyle_class_requestonly_with_attr(self):
        config = self._makeOne()
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return 'OK'
        result = config._map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_newstyle_class_requestonly_with_attr_and_renderer(
        self):
        config = self._makeOne()
        self._registerRenderer(config)
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = config._map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_as_oldstyle_class_context_and_request(self):
        config = self._makeOne()
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = config._map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_oldstyle_class_context_and_request_with_attr(self):
        config = self._makeOne()
        class view:
            def __init__(self, context, request):
                pass
            def index(self):
                return 'OK'
        result = config._map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_oldstyle_class_context_and_request_attr_and_renderer(
        self):
        config = self._makeOne()
        self._registerRenderer(config)
        class view:
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = config._map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_as_oldstyle_class_requestonly(self):
        config = self._makeOne()
        class view:
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        result = config._map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_oldstyle_class_requestonly_with_attr(self):
        config = self._makeOne()
        class view:
            def __init__(self, request):
                pass
            def index(self):
                return 'OK'
        result = config._map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_oldstyle_class_requestonly_attr_and_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config)
        class view:
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = config._map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_as_instance_context_and_request(self):
        config = self._makeOne()
        class View:
            def __call__(self, context, request):
                return 'OK'
        view = View()
        result = config._map_view(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')
        
    def test__map_view_as_instance_context_and_request_and_attr(self):
        config = self._makeOne()
        class View:
            def index(self, context, request):
                return 'OK'
        view = View()
        result = config._map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_instance_context_and_request_attr_and_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config)
        class View:
            def index(self, context, request):
                return {'a':'1'}
        view = View()
        result = config._map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_as_instance_requestonly(self):
        config = self._makeOne()
        class View:
            def __call__(self, request):
                return 'OK'
        view = View()
        result = config._map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_instance_requestonly_with_attr(self):
        config = self._makeOne()
        class View:
            def index(self, request):
                return 'OK'
        view = View()
        result = config._map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_instance_requestonly_with_attr_and_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config)
        class View:
            def index(self, request):
                return {'a':'1'}
        view = View()
        result = config._map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_rendereronly(self):
        config = self._makeOne()
        self._registerRenderer(config)
        def view(context, request):
            return {'a':'1'}
        result = config._map_view(
            view,
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_defaultrendereronly(self):
        config = self._makeOne()
        self._registerRenderer(config, name='')
        def view(context, request):
            return {'a':'1'}
        result = config._map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_default_config_fixtureapp_default_filename_withpackage(self):
        manager = DummyRegistryManager()
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callDefaultConfiguration(rootfactory, fixtureapp)
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failUnless(registry.queryUtility(IFixture)) # only in c.zcml

    def test_default_config_fixtureapp_explicit_filename(self):
        manager = DummyRegistryManager()
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, filename='another.zcml',
            manager=manager)
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(registry.queryUtility(IFixture)) # only in c.zcml

    def test_default_config_fixtureapp_explicit_filename_in_settings(self):
        import os
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = os.path.join(os.path.dirname(fixtureapp.__file__),
                                'another.zcml')
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, filename='configure.zcml',
            settings={'configure_zcml':zcmlfile},
            manager=manager)
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(registry.queryUtility(IFixture)) # only in c.zcml

    def test_default_config_fixtureapp_explicit_specification_in_settings(self):
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = 'repoze.bfg.tests.fixtureapp.subpackage:yetanother.zcml'
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, filename='configure.zcml',
            settings={'configure_zcml':zcmlfile},
            manager=manager)
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(registry.queryUtility(IFixture)) # only in c.zcml

    def test_default_config_fixtureapp_filename_hascolon_isabs(self):
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = 'repoze.bfg.tests.fixtureapp.subpackage:yetanother.zcml'
        class Dummy:
            def isabs(self, name):
                return True
        os = Dummy()
        os.path = Dummy()
        self.assertRaises(IOError, self._callDefaultConfiguration,
                          rootfactory,
                          fixtureapp,
                          filename='configure.zcml',
                          settings={'configure_zcml':zcmlfile},
                          manager=manager,
                          os=os)
        
    def test_default_config_custom_settings(self):
        manager = DummyRegistryManager()
        settings = {'mysetting':True}
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, settings=settings,
            manager=manager)
        from repoze.bfg.interfaces import ISettings
        settings = registry.getUtility(ISettings)
        self.assertEqual(settings.reload_templates, False)
        self.assertEqual(settings.debug_authorization, False)
        self.assertEqual(settings.mysetting, True)

    def test_default_config_registrations(self):
        manager = DummyRegistryManager()
        settings = {'reload_templates':True,
                    'debug_authorization':True}
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, settings=settings,
            manager=manager)
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        settings = registry.getUtility(ISettings)
        logger = registry.getUtility(ILogger, name='repoze.bfg.debug')
        rootfactory = registry.getUtility(IRootFactory)
        self.assertEqual(logger.name, 'repoze.bfg.debug')
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_authorization, True)
        self.assertEqual(rootfactory, rootfactory)
        self.failUnless(manager.pushed and manager.popped)

    def test_default_config_routes_in_config(self):
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        from repoze.bfg.interfaces import IRoutesMapper
        settings = {'reload_templates':True,
                    'debug_authorization':True}
        from repoze.bfg.tests import routesapp
        rootfactory = DummyRootFactory(None)
        registry = self._callDefaultConfiguration(
            rootfactory, routesapp, settings=settings)
        settings = registry.getUtility(ISettings)
        logger = registry.getUtility(ILogger, name='repoze.bfg.debug')
        self.assertEqual(registry.getUtility(IRootFactory), rootfactory)
        self.failUnless(registry.getUtility(IRoutesMapper))

    def test_default_config_lock_and_unlock(self):
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        dummylock = DummyLock()
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, filename='configure.zcml',
            lock=dummylock)
        self.assertEqual(dummylock.acquired, True)
        self.assertEqual(dummylock.released, True)

class TestBFGViewGrokker(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.configuration import BFGViewGrokker
        return BFGViewGrokker

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_grok_is_bfg_view(self):
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from zope.interface import Interface
        from repoze.bfg.configuration import Configurator
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
        config = Configurator(sm)
        result = grokker.grok('name', obj, _info='', _configurator=config)
        self.assertEqual(result, True)
        wrapped = sm.adapters.lookup((Interface, IRequest), IView,
                                     name='foo.html')
        self.assertEqual(wrapped(None, None), 'OK')

    def test_grok_is_not_bfg_view(self):
        grokker = self._makeOne()
        class obj:
            pass
        context = DummyContext()
        result = grokker.grok('name', obj)
        self.assertEqual(result, False)

class TestDefaultRootFactory(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.configuration import DefaultRootFactory
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

    

class DummyRequest:
    pass

class DummyRegistryManager:
    def push(self, registry):
        from repoze.bfg.threadlocal import manager
        manager.push(registry)
        self.pushed = True

    def pop(self):
        from repoze.bfg.threadlocal import manager
        manager.pop()
        self.popped = True

class DummyRootFactory:
    def __init__(self, root):
        self.root = root

class DummyContext:
    pass

class DummyLock:
    def acquire(self):
        self.acquired = True

    def release(self):
        self.released = True
        
class DummyPackage:
    def __init__(self, name):
        self.__name__ = name

class DummyOverrides:
    def __init__(self, package):
        self.package = package
        self.inserted = []

    def insert(self, path, package, prefix):
        self.inserted.append((path, package, prefix))

from zope.interface import Interface
class IDummy(Interface):
    pass

class IOther(Interface):
    pass
