import unittest

class TestPShellCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.paster import PShellCommand
        return PShellCommand

    def _makeOne(self):
        return self._getTargetClass()('pshell')

    def test_command_ipshell_is_None_ipython_enabled(self):
        command = self._makeOne()
        interact = DummyInteractor()
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        command.interact = (interact,)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp')
        class Options(object): pass
        command.options = Options()
        command.options.disable_ipython = False
        command.command(IPShell=None)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.assertTrue(loadapp.relative_to)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['registry'], dummy_registry)
        self.assertEqual(pushed['request'].registry, dummy_registry)
        self.assertEqual(interact.local, {'root':dummy_root,
                                          'registry':dummy_registry})
        self.assertTrue(interact.banner)
        self.assertEqual(len(app.threadlocal_manager.popped), 1)

    def test_command_ipshell_is_not_None_ipython_disabled(self):
        command = self._makeOne()
        interact = DummyInteractor()
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        command.interact = (interact,)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp')
        class Options(object): pass
        command.options = Options()
        command.options.disable_ipython = True
        command.command(IPShell='notnone')
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.assertTrue(loadapp.relative_to)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['registry'], dummy_registry)
        self.assertEqual(pushed['request'].registry, dummy_registry)
        self.assertEqual(interact.local, {'root':dummy_root,
                                          'registry':dummy_registry})
        self.assertTrue(interact.banner)
        self.assertEqual(len(app.threadlocal_manager.popped), 1)

    def test_command_ipython_enabled(self):
        command = self._makeOne()
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        dummy_shell_factory = DummyIPShellFactory()
        command.args = ('/foo/bar/myapp.ini#myapp')
        class Options(object): pass
        command.options = Options()
        command.options.disable_ipython = False
        command.command(IPShell=dummy_shell_factory)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.assertTrue(loadapp.relative_to)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['registry'], dummy_registry)
        self.assertEqual(pushed['request'].registry, dummy_registry)
        self.assertEqual(dummy_shell_factory.shell.local_ns,
                         {'root':dummy_root, 'registry':dummy_registry})
        self.assertEqual(dummy_shell_factory.shell.global_ns, {})
        self.assertTrue('\n\n' in dummy_shell_factory.shell.IP.BANNER)
        self.assertEqual(len(app.threadlocal_manager.popped), 1)

    def test_command_get_app_hookable(self):
        from paste.deploy import loadapp
        command = self._makeOne()
        app = DummyApp()
        apped = []
        def get_app(*arg, **kw):
            apped.append((arg, kw))
            return app
        command.get_app = get_app
        interact = DummyInteractor()
        app = DummyApp()
        command.interact = (interact,)
        command.args = ('/foo/bar/myapp.ini#myapp')
        class Options(object): pass
        command.options = Options()
        command.options.disable_ipython =True
        command.command(IPShell=None)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['registry'], dummy_registry)
        self.assertEqual(pushed['request'].registry, dummy_registry)
        self.assertEqual(interact.local, {'root':dummy_root,
                                          'registry':dummy_registry})
        self.assertTrue(interact.banner)
        self.assertEqual(len(app.threadlocal_manager.popped), 1)
        self.assertEqual(apped, [(('/foo/bar/myapp.ini', 'myapp'),
                                  {'loadapp': loadapp})])

    def test_command_get_root_hookable(self):
        command = self._makeOne()
        interact = DummyInteractor()
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        command.interact = (interact,)
        command.loadapp = (loadapp,)
        root = Dummy()
        apps = []
        def get_root(app):
            apps.append(app)
            return root, lambda *arg: None
        command.get_root =get_root
        command.args = ('/foo/bar/myapp.ini#myapp')
        class Options(object): pass
        command.options = Options()
        command.options.disable_ipython =True
        command.command(IPShell=None)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.assertTrue(loadapp.relative_to)
        self.assertEqual(len(app.threadlocal_manager.pushed), 0)
        self.assertEqual(interact.local, {'root':root,
                                          'registry':dummy_registry})
        self.assertTrue(interact.banner)
        self.assertEqual(apps, [app])

class TestPRoutesCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.paster import PRoutesCommand
        return PRoutesCommand

    def _makeOne(self):
        return self._getTargetClass()('proutes')

    def test_no_routes(self):
        command = self._makeOne()
        mapper = DummyMapper()
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L, [])

    def test_no_mapper(self):
        command = self._makeOne()
        command._get_mapper = lambda *arg:None
        L = []
        command.out = L.append
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp')
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
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp')
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
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp')
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
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp')
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
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(len(L), 3)
        self.assertEqual(L[-1].split()[:3], ['a', '/a', '<unknown>'])

    def test__get_mapper(self):
        from pyramid.registry import Registry
        from pyramid.urldispatch import RoutesMapper
        command = self._makeOne()
        registry = Registry()
        class App: pass
        app = App()
        app.registry = registry
        result = command._get_mapper(app)
        self.assertEqual(result.__class__, RoutesMapper)
        
class TestPViewsCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.paster import PViewsCommand
        return PViewsCommand

    def _makeOne(self):
        return self._getTargetClass()('pviews')

    def failUnless(self, condition):
        # silence stupid deprecation under Python >= 2.7
        self.assertTrue(condition)

    def test__find_view_no_match(self):
        from pyramid.registry import Registry
        registry = Registry()
        self._register_mapper(registry, [])
        command = self._makeOne()
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
        command = self._makeOne()
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
        command = self._makeOne()
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
        command = self._makeOne()
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
        command = self._makeOne()
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
        command = self._makeOne()
        result = command._find_view('/a', registry)
        self.failUnless(IMultiView.providedBy(result))

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
        command = self._makeOne()
        result = command._find_view('/a', registry)
        self.failUnless(IMultiView.providedBy(result))
        self.assertEqual(len(result.views), 2)
        self.failUnless((None, view1, None) in result.views)
        self.failUnless((None, view2, None) in result.views)

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
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        command._find_view = lambda arg1, arg2: None
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    Not found.')

    def test_views_command_not_found_url_starts_without_slash(self):
        from pyramid.registry import Registry
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        command._find_view = lambda arg1, arg2: None
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp', 'a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    Not found.')

    def test_views_command_single_view_traversal(self):
        from pyramid.registry import Registry
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        view = DummyView(context='context', view_name='a')
        command._find_view = lambda arg1, arg2: view
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.DummyView')

    def test_views_command_single_view_function_traversal(self):
        from pyramid.registry import Registry
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        def view(): pass
        view.__request_attrs__ = {'context': 'context', 'view_name': 'a'}
        command._find_view = lambda arg1, arg2: view
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.view')

    def test_views_command_single_view_traversal_with_permission(self):
        from pyramid.registry import Registry
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        view = DummyView(context='context', view_name='a')
        view.__permission__ = 'test'
        command._find_view = lambda arg1, arg2: view
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
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
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        def predicate(): pass
        predicate.__text__ = "predicate = x"
        view = DummyView(context='context', view_name='a')
        view.__predicates__ = [predicate]
        command._find_view = lambda arg1, arg2: view
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
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
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        route = DummyRoute('a', '/a', matchdict={})
        view = DummyView(context='context', view_name='a',
                         matched_route=route, subpath='')
        command._find_view = lambda arg1, arg2: view
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
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
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        view1 = DummyView(context='context', view_name='a1')
        view1.__name__ = 'view1'
        view1.__view_attr__ = 'call'
        multiview1 = DummyMultiView(view1, context='context', view_name='a1')
        multiview2 = DummyMultiView(multiview1, context='context',
                                    view_name='a')
        command._find_view = lambda arg1, arg2: multiview2
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
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
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        def predicate(): pass
        predicate.__text__ = "predicate = x"
        route = DummyRoute('a', '/a', matchdict={}, predicate=predicate)
        view = DummyView(context='context', view_name='a',
                         matched_route=route, subpath='')
        command._find_view = lambda arg1, arg2: view
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
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
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        view = DummyView(context='context')
        view.__name__ = 'view'
        view.__view_attr__ = 'call'
        multiview = DummyMultiView(view, context='context', view_name='a')
        command._find_view = lambda arg1, arg2: multiview
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.view.call')

    def test_views_command_multiview_with_permission(self):
        from pyramid.registry import Registry
        command = self._makeOne()
        registry = Registry()
        L = []
        command.out = L.append
        view = DummyView(context='context')
        view.__name__ = 'view'
        view.__view_attr__ = 'call'
        view.__permission__ = 'test'
        multiview = DummyMultiView(view, context='context', view_name='a')
        command._find_view = lambda arg1, arg2: multiview
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
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
        command = self._makeOne()
        registry = Registry()
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
        app = DummyApp()
        app.registry = registry
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini#myapp', '/a')
        result = command.command()
        self.assertEqual(result, None)
        self.assertEqual(L[1], 'URL = /a')
        self.assertEqual(L[3], '    context: context')
        self.assertEqual(L[4], '    view name: a')
        self.assertEqual(L[8], '    pyramid.tests.test_paster.view.call')
        self.assertEqual(L[9], '    view predicates (predicate = x)')

    def _register_mapper(self, registry, routes):
        from pyramid.interfaces import IRoutesMapper
        mapper = DummyMapper(*routes)
        registry.registerUtility(mapper, IRoutesMapper)

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
        self.threadlocal_manager = DummyThreadLocalManager()

    def root_factory(self, environ):
        return dummy_root

class DummyThreadLocalManager:
    def __init__(self):
        self.pushed = []
        self.popped = []
        
    def push(self, item):
        self.pushed.append(item)

    def pop(self):
        self.popped.append(True)
        
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

