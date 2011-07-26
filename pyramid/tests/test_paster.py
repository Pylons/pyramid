import unittest

class TestPShellCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.paster import PShellCommand
        return PShellCommand

    def _makeOne(self, patch_interact=True, patch_bootstrap=True,
                 patch_config=True, patch_args=True, patch_options=True):
        cmd = self._getTargetClass()('pshell')
        if patch_interact:
            self.interact = DummyInteractor()
            cmd.interact = (self.interact,)
        if patch_bootstrap:
            self.bootstrap = DummyBootstrap()
            cmd.bootstrap = (self.bootstrap,)
        if patch_config:
            self.config_factory = DummyConfigParserFactory()
            cmd.ConfigParser = self.config_factory
        if patch_args:
            self.args = ('/foo/bar/myapp.ini#myapp',)
            cmd.args = self.args
        if patch_options:
            class Options(object): pass
            self.options = Options()
            self.options.disable_ipython = True
            cmd.options = self.options
        return cmd

    def test_command_ipshell_is_None_ipython_enabled(self):
        command = self._makeOne()
        command.options.disable_ipython = True
        command.command(IPShell=None)
        self.assertTrue(self.config_factory.parser)
        self.assertEqual(self.config_factory.parser.filename,
                         '/foo/bar/myapp.ini')
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(self.interact.local, {
            'app':self.bootstrap.app, 'root':self.bootstrap.root,
            'registry':self.bootstrap.registry,
            'request':self.bootstrap.request,
            'root_factory':self.bootstrap.root_factory,
        })
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(self.interact.banner)

    def test_command_ipshell_is_not_None_ipython_disabled(self):
        command = self._makeOne()
        command.options.disable_ipython = True
        command.command(IPShell='notnone')
        self.assertTrue(self.config_factory.parser)
        self.assertEqual(self.config_factory.parser.filename,
                         '/foo/bar/myapp.ini')
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(self.interact.local, {
            'app':self.bootstrap.app, 'root':self.bootstrap.root,
            'registry':self.bootstrap.registry,
            'request':self.bootstrap.request,
            'root_factory':self.bootstrap.root_factory,
        })
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(self.interact.banner)

    def test_command_ipython_enabled(self):
        command = self._makeOne(patch_interact=False)
        command.options.disable_ipython = False
        dummy_shell_factory = DummyIPShellFactory()
        command.command(IPShell=dummy_shell_factory)
        self.assertTrue(self.config_factory.parser)
        self.assertEqual(self.config_factory.parser.filename,
                         '/foo/bar/myapp.ini')
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(dummy_shell_factory.shell.local_ns, {
            'app':self.bootstrap.app, 'root':self.bootstrap.root,
            'registry':self.bootstrap.registry,
            'request':self.bootstrap.request,
            'root_factory':self.bootstrap.root_factory,
        })
        self.assertEqual(dummy_shell_factory.shell.global_ns, {})
        self.assertTrue(self.bootstrap.closer.called)

    def test_command_loads_custom_items(self):
        command = self._makeOne()
        model = Dummy()
        self.config_factory.items = [('m', model)]
        command.options.disable_ipython = True
        command.command(IPShell=None)
        self.assertTrue(self.config_factory.parser)
        self.assertEqual(self.config_factory.parser.filename,
                         '/foo/bar/myapp.ini')
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(self.interact.local, {
            'app':self.bootstrap.app, 'root':self.bootstrap.root,
            'registry':self.bootstrap.registry,
            'request':self.bootstrap.request,
            'root_factory':self.bootstrap.root_factory,
            'm':model,
        })
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(self.interact.banner)

    def test_command_custom_section_override(self):
        command = self._makeOne()
        dummy = Dummy()
        self.config_factory.items = [('app', dummy), ('root', dummy),
                                     ('registry', dummy), ('request', dummy)]
        command.options.disable_ipython = True
        command.command(IPShell=None)
        self.assertTrue(self.config_factory.parser)
        self.assertEqual(self.config_factory.parser.filename,
                         '/foo/bar/myapp.ini')
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(self.interact.local, {
            'app':dummy, 'root':dummy, 'registry':dummy, 'request':dummy,
            'root_factory':self.bootstrap.root_factory,
        })
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(self.interact.banner)

class TestPRoutesCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.paster import PRoutesCommand
        return PRoutesCommand

    def _makeOne(self):
        cmd = self._getTargetClass()('proutes')
        cmd.bootstrap = (DummyBootstrap(),)
        cmd.args = ('/foo/bar/myapp.ini#myapp',)
        return cmd

    def test_no_routes(self):
        command = self._makeOne()
        mapper = DummyMapper()
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L, [])

    def test_no_mapper(self):
        command = self._makeOne()
        command._get_mapper = lambda *arg:None
        L = []
        command.out = L.append
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L, [])

    def test_single_route_no_route_registered(self):
        command = self._makeOne()
        route = DummyRoute('a', '/a')
        mapper = DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(len(L), 3)
        self.assertEqual(L[-1].split(), ['a', '/a', '<unknown>'])

    def test_single_route_no_views_registered(self):
        from zope.interface import Interface
        from pyramid.registry import Registry
        from pyramid.interfaces import IRouteRequest
        registry = Registry()
        def view():pass
        class IMyRoute(Interface):
            pass
        registry.registerUtility(IMyRoute, IRouteRequest, name='a')
        command = self._makeOne()
        route = DummyRoute('a', '/a')
        mapper = DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        command.bootstrap = (DummyBootstrap(registry=registry),)
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(len(L), 3)
        self.assertEqual(L[-1].split()[:3], ['a', '/a', 'None'])

    def test_single_route_one_view_registered(self):
        from zope.interface import Interface
        from pyramid.registry import Registry
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView
        registry = Registry()
        def view():pass
        class IMyRoute(Interface):
            pass
        registry.registerAdapter(view,
                                 (IViewClassifier, IMyRoute, Interface),
                                 IView, '')
        registry.registerUtility(IMyRoute, IRouteRequest, name='a')
        command = self._makeOne()
        route = DummyRoute('a', '/a')
        mapper = DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        command.bootstrap = (DummyBootstrap(registry=registry),)
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(len(L), 3)
        self.assertEqual(L[-1].split()[:4], ['a', '/a', '<function', 'view'])
        
    def test_single_route_one_view_registered_with_factory(self):
        from zope.interface import Interface
        from pyramid.registry import Registry
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView
        registry = Registry()
        def view():pass
        class IMyRoot(Interface):
            pass
        class IMyRoute(Interface):
            pass
        registry.registerAdapter(view,
                                 (IViewClassifier, IMyRoute, IMyRoot),
                                 IView, '')
        registry.registerUtility(IMyRoute, IRouteRequest, name='a')
        command = self._makeOne()
        def factory(request): pass
        route = DummyRoute('a', '/a', factory=factory)
        mapper = DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        command.bootstrap = (DummyBootstrap(registry=registry),)
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(len(L), 3)
        self.assertEqual(L[-1].split()[:3], ['a', '/a', '<unknown>'])

    def test__get_mapper(self):
        from pyramid.registry import Registry
        from pyramid.urldispatch import RoutesMapper
        command = self._makeOne()
        registry = Registry()
        result = command._get_mapper(registry)
        self.assertEqual(result.__class__, RoutesMapper)
        
class TestPViewsCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.paster import PViewsCommand
        return PViewsCommand

    def _makeOne(self, registry=None):
        cmd = self._getTargetClass()('pviews')
        cmd.bootstrap = (DummyBootstrap(registry=registry),)
        cmd.args = ('/foo/bar/myapp.ini#myapp',)
        return cmd

    def _register_mapper(self, registry, routes):
        from pyramid.interfaces import IRoutesMapper
        mapper = DummyMapper(*routes)
        registry.registerUtility(mapper, IRoutesMapper)

    def test__find_view_no_match(self):
        from pyramid.registry import Registry
        registry = Registry()
        self._register_mapper(registry, [])
        command = self._makeOne(registry)
        result = command._find_view('/a', registry)
        self.assertEqual(result, None)

    def test__find_view_no_match_multiview_registered(self):
        from zope.interface import implements
        from zope.interface import providedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IMultiView
        from pyramid.traversal import DefaultRootFactory
        from pyramid.registry import Registry
        registry = Registry()
        class View1(object):
            implements(IMultiView)
        request = DummyRequest({'PATH_INFO':'/a'})
        root = DefaultRootFactory(request)
        root_iface = providedBy(root)
        registry.registerAdapter(View1(),
                                 (IViewClassifier, IRequest, root_iface),
                                 IMultiView)
        self._register_mapper(registry, [])
        command = self._makeOne(registry=registry)
        result = command._find_view('/x', registry)
        self.assertEqual(result, None)

    def test__find_view_traversal(self):
        from zope.interface import providedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView
        from pyramid.traversal import DefaultRootFactory
        from pyramid.registry import Registry
        registry = Registry()
        def view1(): pass
        request = DummyRequest({'PATH_INFO':'/a'})
        root = DefaultRootFactory(request)
        root_iface = providedBy(root)
        registry.registerAdapter(view1,
                                 (IViewClassifier, IRequest, root_iface),
                                 IView, name='a')
        self._register_mapper(registry, [])
        command = self._makeOne(registry=registry)
        result = command._find_view('/a', registry)
        self.assertEqual(result, view1)

    def test__find_view_traversal_multiview(self):
        from zope.interface import implements
        from zope.interface import providedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IMultiView
        from pyramid.traversal import DefaultRootFactory
        from pyramid.registry import Registry
        registry = Registry()
        class View1(object):
            implements(IMultiView)
        request = DummyRequest({'PATH_INFO':'/a'})
        root = DefaultRootFactory(request)
        root_iface = providedBy(root)
        view = View1()
        registry.registerAdapter(view,
                                 (IViewClassifier, IRequest, root_iface),
                                 IMultiView, name='a')
        self._register_mapper(registry, [])
        command = self._makeOne(registry=registry)
        result = command._find_view('/a', registry)
        self.assertEqual(result, view)

    def test__find_view_route_no_multiview(self):
        from zope.interface import Interface
        from zope.interface import implements
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView
        from pyramid.registry import Registry
        registry = Registry()
        def view():pass
        class IMyRoot(Interface):
            pass
        class IMyRoute(Interface):
            pass
        registry.registerAdapter(view,
                                 (IViewClassifier, IMyRoute, IMyRoot),
                                 IView, '')
        registry.registerUtility(IMyRoute, IRouteRequest, name='a')
        class Factory(object):
            implements(IMyRoot)
            def __init__(self, request):
                pass
        routes = [DummyRoute('a', '/a', factory=Factory, matchdict={}),
                  DummyRoute('b', '/b', factory=Factory)]
        self._register_mapper(registry, routes)
        command = self._makeOne(registry=registry)
        result = command._find_view('/a', registry)
        self.assertEqual(result, view)

    def test__find_view_route_multiview_no_view_registered(self):
        from zope.interface import Interface
        from zope.interface import implements
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IRootFactory
        from pyramid.registry import Registry
        registry = Registry()
        def view1():pass
        def view2():pass
        class IMyRoot(Interface):
            pass
        class IMyRoute1(Interface):
            pass
        class IMyRoute2(Interface):
            pass
        registry.registerUtility(IMyRoute1, IRouteRequest, name='a')
        registry.registerUtility(IMyRoute2, IRouteRequest, name='b')
        class Factory(object):
            implements(IMyRoot)
            def __init__(self, request):
                pass
        registry.registerUtility(Factory, IRootFactory)
        routes = [DummyRoute('a', '/a', matchdict={}),
                  DummyRoute('b', '/a', matchdict={})]
        self._register_mapper(registry, routes)
        command = self._makeOne(registry=registry)
        result = command._find_view('/a', registry)
        self.assertTrue(IMultiView.providedBy(result))

    def test__find_view_route_multiview(self):
        from zope.interface import Interface
        from zope.interface import implements
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IRootFactory
        from pyramid.registry import Registry
        registry = Registry()
        def view1():pass
        def view2():pass
        class IMyRoot(Interface):
            pass
        class IMyRoute1(Interface):
            pass
        class IMyRoute2(Interface):
            pass
        registry.registerAdapter(view1,
                                 (IViewClassifier, IMyRoute1, IMyRoot),
                                 IView, '')
        registry.registerAdapter(view2,
                                 (IViewClassifier, IMyRoute2, IMyRoot),
                                 IView, '')
        registry.registerUtility(IMyRoute1, IRouteRequest, name='a')
        registry.registerUtility(IMyRoute2, IRouteRequest, name='b')
        class Factory(object):
            implements(IMyRoot)
            def __init__(self, request):
                pass
        registry.registerUtility(Factory, IRootFactory)
        routes = [DummyRoute('a', '/a', matchdict={}),
                  DummyRoute('b', '/a', matchdict={})]
        self._register_mapper(registry, routes)
        command = self._makeOne(registry=registry)
        result = command._find_view('/a', registry)
        self.assertTrue(IMultiView.providedBy(result))
        self.assertEqual(len(result.views), 2)
        self.assertTrue((None, view1, None) in result.views)
        self.assertTrue((None, view2, None) in result.views)

    def test__find_multi_routes_all_match(self):
        command = self._makeOne()
        def factory(request): pass
        routes = [DummyRoute('a', '/a', factory=factory, matchdict={}),
                  DummyRoute('b', '/a', factory=factory, matchdict={})]
        mapper = DummyMapper(*routes)
        request = DummyRequest({'PATH_INFO':'/a'})
        result = command._find_multi_routes(mapper, request)
        self.assertEqual(result, [{'match':{}, 'route':routes[0]},
                                  {'match':{}, 'route':routes[1]}])
        
    def test__find_multi_routes_some_match(self):
        command = self._makeOne()
        def factory(request): pass
        routes = [DummyRoute('a', '/a', factory=factory),
                  DummyRoute('b', '/a', factory=factory, matchdict={})]
        mapper = DummyMapper(*routes)
        request = DummyRequest({'PATH_INFO':'/a'})
        result = command._find_multi_routes(mapper, request)
        self.assertEqual(result, [{'match':{}, 'route':routes[1]}])
        
    def test__find_multi_routes_none_match(self):
        command = self._makeOne()
        def factory(request): pass
        routes = [DummyRoute('a', '/a', factory=factory),
                  DummyRoute('b', '/a', factory=factory)]
        mapper = DummyMapper(*routes)
        request = DummyRequest({'PATH_INFO':'/a'})
        result = command._find_multi_routes(mapper, request)
        self.assertEqual(result, [])
        
    def test_views_command_not_found(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        command._find_view = lambda arg1, arg2: None
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    Not found.')

    def test_views_command_not_found_url_starts_without_slash(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        command._find_view = lambda arg1, arg2: None
        command.args = ('/foo/bar/myapp.ini#myapp', 'a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    Not found.')

    def test_views_command_single_view_traversal(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        view = DummyView(context='context', view_name='a')
        command._find_view = lambda arg1, arg2: view
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.DummyView')

    def test_views_command_single_view_function_traversal(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        def view(): pass
        view.__request_attrs__ = {'context': 'context', 'view_name': 'a'}
        command._find_view = lambda arg1, arg2: view
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.view')

    def test_views_command_single_view_traversal_with_permission(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        view = DummyView(context='context', view_name='a')
        view.__permission__ = 'test'
        command._find_view = lambda arg1, arg2: view
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.DummyView')
        self.assertEqual(L[9], '    required permission = test')

    def test_views_command_single_view_traversal_with_predicates(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        def predicate(): pass
        predicate.__text__ = "predicate = x"
        view = DummyView(context='context', view_name='a')
        view.__predicates__ = [predicate]
        command._find_view = lambda arg1, arg2: view
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.DummyView')
        self.assertEqual(L[9], '    view predicates (predicate = x)')

    def test_views_command_single_view_route(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        route = DummyRoute('a', '/a', matchdict={})
        view = DummyView(context='context', view_name='a',
                         matched_route=route, subpath='')
        command._find_view = lambda arg1, arg2: view
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[6], '    Route:')
        self.assertEqual(L[8], '    route name: a')
        self.assertEqual(L[9], '    route pattern: /a')
        self.assertEqual(L[10], '    route path: /a')
        self.assertEqual(L[11], '    subpath: ')
        self.assertEqual(L[15], '        pyramid.tests.test_paster.DummyView')

    def test_views_command_multi_view_nested(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        view1 = DummyView(context='context', view_name='a1')
        view1.__name__ = 'view1'
        view1.__view_attr__ = 'call'
        multiview1 = DummyMultiView(view1, context='context', view_name='a1')
        multiview2 = DummyMultiView(multiview1, context='context',
                                    view_name='a')
        command._find_view = lambda arg1, arg2: multiview2
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.DummyMultiView')
        self.assertEqual(L[12], '        pyramid.tests.test_paster.view1.call')

    def test_views_command_single_view_route_with_route_predicates(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        def predicate(): pass
        predicate.__text__ = "predicate = x"
        route = DummyRoute('a', '/a', matchdict={}, predicate=predicate)
        view = DummyView(context='context', view_name='a',
                         matched_route=route, subpath='')
        command._find_view = lambda arg1, arg2: view
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[6], '    Route:')
        self.assertEqual(L[8], '    route name: a')
        self.assertEqual(L[9], '    route pattern: /a')
        self.assertEqual(L[10], '    route path: /a')
        self.assertEqual(L[11], '    subpath: ')
        self.assertEqual(L[12], '    route predicates (predicate = x)')
        self.assertEqual(L[16], '        pyramid.tests.test_paster.DummyView')

    def test_views_command_multiview(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        view = DummyView(context='context')
        view.__name__ = 'view'
        view.__view_attr__ = 'call'
        multiview = DummyMultiView(view, context='context', view_name='a')
        command._find_view = lambda arg1, arg2: multiview
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.view.call')

    def test_views_command_multiview_with_permission(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        view = DummyView(context='context')
        view.__name__ = 'view'
        view.__view_attr__ = 'call'
        view.__permission__ = 'test'
        multiview = DummyMultiView(view, context='context', view_name='a')
        command._find_view = lambda arg1, arg2: multiview
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.view.call')
        self.assertEqual(L[9], '    required permission = test')

    def test_views_command_multiview_with_predicates(self):
        from pyramid.registry import Registry
        registry = Registry()
        command = self._makeOne(registry=registry)
        L = []
        command.out = L.append
        def predicate(): pass
        predicate.__text__ = "predicate = x"
        view = DummyView(context='context')
        view.__name__ = 'view'
        view.__view_attr__ = 'call'
        view.__predicates__ = [predicate]
        multiview = DummyMultiView(view, context='context', view_name='a')
        command._find_view = lambda arg1, arg2: multiview
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.view.call')
        self.assertEqual(L[9], '    view predicates (predicate = x)')

class TestGetApp(unittest.TestCase):
    def _callFUT(self, config_file, section_name, loadapp):
        from pyramid.paster import get_app
        return get_app(config_file, section_name, loadapp)

    def test_it(self):
        import os
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        result = self._callFUT('/foo/bar/myapp.ini', 'myapp', loadapp)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.assertEqual(loadapp.relative_to, os.getcwd())
        self.assertEqual(result, app)

    def test_it_with_hash(self):
        import os
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        result = self._callFUT('/foo/bar/myapp.ini#myapp', None, loadapp)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.assertEqual(loadapp.relative_to, os.getcwd())
        self.assertEqual(result, app)

    def test_it_with_hash_and_name_override(self):
        import os
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        result = self._callFUT('/foo/bar/myapp.ini#myapp', 'yourapp', loadapp)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'yourapp')
        self.assertEqual(loadapp.relative_to, os.getcwd())
        self.assertEqual(result, app)

class TestBootstrap(unittest.TestCase):
    def _callFUT(self, config_uri, request=None):
        from pyramid.paster import bootstrap
        return bootstrap(config_uri, request)

    def setUp(self):
        import pyramid.paster
        self.original_get_app = pyramid.paster.get_app
        self.original_prepare = pyramid.paster.prepare
        self.app = app = DummyApp()
        self.root = root = Dummy()

        class DummyGetApp(object):
            def __call__(self, *a, **kw):
                self.a = a
                self.kw = kw
                return app
        self.get_app = pyramid.paster.get_app = DummyGetApp()

        class DummyPrepare(object):
            def __call__(self, *a, **kw):
                self.a = a
                self.kw = kw
                return {'root':root, 'closer':lambda: None}
        self.getroot = pyramid.paster.prepare = DummyPrepare()

    def tearDown(self):
        import pyramid.paster
        pyramid.paster.get_app = self.original_get_app
        pyramid.paster.prepare = self.original_prepare

    def test_it_request_with_registry(self):
        request = DummyRequest({})
        request.registry = dummy_registry
        result = self._callFUT('/foo/bar/myapp.ini', request)
        self.assertEqual(result['app'], self.app)
        self.assertEqual(result['root'], self.root)
        self.assert_('closer' in result)

class Dummy:
    pass

class DummyIPShellFactory(object):
    def __call__(self, argv, user_ns=None):
        shell = DummyIPShell()
        shell(user_ns, {})
        self.shell = shell
        return shell

class DummyIPShell(object):
    IP = Dummy()
    IP.BANNER = 'foo'
    def __call__(self, local_ns, global_ns):
        self.local_ns = local_ns
        self.global_ns = global_ns

    def mainloop(self):
        pass

dummy_root = Dummy()

class DummyRegistry(object):
    settings = {}
    def queryUtility(self, iface, default=None, name=''):
        return default

dummy_registry = DummyRegistry()

class DummyInteractor:
    def __call__(self, banner, local):
        self.banner = banner
        self.local = local

class DummyLoadApp:
    def __init__(self, app):
        self.app = app

    def __call__(self, config_name, name=None, relative_to=None):
        self.config_name = config_name
        self.section_name = name
        self.relative_to = relative_to
        return self.app

class DummyApp:
    def __init__(self):
        self.registry = dummy_registry

class DummyMapper(object):
    def __init__(self, *routes):
        self.routes = routes

    def get_routes(self):
        return self.routes

class DummyRoute(object):
    def __init__(self, name, pattern, factory=None,
                 matchdict=None, predicate=None):
        self.name = name
        self.path = pattern
        self.pattern = pattern
        self.factory = factory
        self.matchdict = matchdict
        self.predicates = []
        if predicate is not None:
            self.predicates = [predicate]

    def match(self, route):
        return self.matchdict
        
class DummyRequest:
    application_url = 'http://example.com:5432'
    script_name = ''
    def __init__(self, environ):
        self.environ = environ
        self.matchdict = {}

class DummyView(object):
    def __init__(self, **attrs):
        self.__request_attrs__ = attrs

class DummyMultiView(object):
    from zope.interface import implements
    from pyramid.interfaces import IMultiView
    implements(IMultiView)

    def __init__(self, *views, **attrs):
        self.views = [(None, view, None) for view in views]
        self.__request_attrs__ = attrs

class DummyConfigParser(object):
    def __init__(self, result):
        self.result = result

    def read(self, filename):
        self.filename = filename

    def items(self, section):
        self.section = section
        if self.result is None:
            from ConfigParser import NoSectionError
            raise NoSectionError, section
        return self.result

class DummyConfigParserFactory(object):
    items = None

    def __call__(self):
        self.parser = DummyConfigParser(self.items)
        return self.parser

class DummyCloser(object):
    def __call__(self):
        self.called = True

class DummyBootstrap(object):
    def __init__(self, app=None, registry=None, request=None, root=None,
                 root_factory=None, closer=None):
        self.app = app or DummyApp()
        if registry is None:
            registry = DummyRegistry()
        self.registry = registry
        if request is None:
            request = DummyRequest({})
        self.request = request
        if root is None:
            root = Dummy()
        self.root = root
        if root_factory is None:
            root_factory = Dummy()
        self.root_factory = root_factory
        if closer is None:
            closer = DummyCloser()
        self.closer = closer

    def __call__(self, *a, **kw):
        self.a = a
        self.kw = kw
        return {
            'app': self.app,
            'registry': self.registry,
            'request': self.request,
            'root': self.root,
            'root_factory': self.root_factory,
            'closer': self.closer,
        }
