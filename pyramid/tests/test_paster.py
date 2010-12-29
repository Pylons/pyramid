import unittest

class TestPShellCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.paster import PShellCommand
        return PShellCommand

    def _makeOne(self):
        return self._getTargetClass()('pshell')

    def test_command_ipython_disabled(self):
        command = self._makeOne()
        interact = DummyInteractor()
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        command.interact = (interact,)
        command.loadapp = (loadapp,)
        command.args = ('/foo/bar/myapp.ini', 'myapp')
        class Options(object): pass
        command.options = Options()
        command.options.disable_ipython =True
        command.command(IPShell=None)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.failUnless(loadapp.relative_to)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['registry'], dummy_registry)
        self.assertEqual(pushed['request'].registry, dummy_registry)
        self.assertEqual(interact.local, {'root':dummy_root,
                                          'registry':dummy_registry})
        self.failUnless(interact.banner)
        self.assertEqual(len(app.threadlocal_manager.popped), 1)

    def test_command_ipython_enabled(self):
        command = self._makeOne()
        app = DummyApp()
        loadapp = DummyLoadApp(app)
        command.loadapp = (loadapp,)
        dummy_shell_factory = DummyIPShellFactory()
        command.args = ('/foo/bar/myapp.ini', 'myapp')
        class Options(object): pass
        command.options = Options()
        command.options.disable_ipython = False
        command.command(IPShell=dummy_shell_factory)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.failUnless(loadapp.relative_to)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['registry'], dummy_registry)
        self.assertEqual(pushed['request'].registry, dummy_registry)
        self.assertEqual(dummy_shell_factory.shell.local_ns,
                         {'root':dummy_root, 'registry':dummy_registry})
        self.assertEqual(dummy_shell_factory.shell.global_ns, {})
        self.failUnless('\n\n' in dummy_shell_factory.shell.IP.BANNER)
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
        command.args = ('/foo/bar/myapp.ini', 'myapp')
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
        self.failUnless(interact.banner)
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
        command.args = ('/foo/bar/myapp.ini', 'myapp')
        class Options(object): pass
        command.options = Options()
        command.options.disable_ipython =True
        command.command(IPShell=None)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.failUnless(loadapp.relative_to)
        self.assertEqual(len(app.threadlocal_manager.pushed), 0)
        self.assertEqual(interact.local, {'root':root,
                                          'registry':dummy_registry})
        self.failUnless(interact.banner)
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
        command.args = ('/foo/bar/myapp.ini', 'myapp')
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
        command.args = ('/foo/bar/myapp.ini', 'myapp')
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
        command.args = ('/foo/bar/myapp.ini', 'myapp')
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
        command.args = ('/foo/bar/myapp.ini', 'myapp')
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
        command.args = ('/foo/bar/myapp.ini', 'myapp')
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
    def __init__(self, name, pattern, factory=None):
        self.name = name
        self.pattern = pattern
        self.factory = factory
        
