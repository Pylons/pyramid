import unittest
from pyramid.tests.test_scripts import dummy


class DummyIntrospector(object):
    def __init__(self):
        self.relations = {}
        self.introspectables = {}

    def add(self, introspectable):
        cat = introspectable.category_name
        if cat not in self.introspectables:
            self.introspectables[cat] = []

        self.introspectables[cat].append(introspectable)

    def get(self, name, discrim):
        intrs = self.introspectables[name]

        for intr in intrs:
            if intr.discriminator == discrim:
                return intr

    def relate(self, a, b):
        if a not in self.relations:
            self.retlations[a] = []

        self.relations[a].append(b)

    def related(self, a):
        return self.relations.get(a, [])


class TestPRoutesCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.scripts.proutes import PRoutesCommand
        return PRoutesCommand

    def _makeOne(self):
        cmd = self._getTargetClass()([])
        cmd.bootstrap = (dummy.DummyBootstrap(),)
        cmd.args = ('/foo/bar/myapp.ini#myapp',)
        return cmd

    def _makeRegistry(self):
        from pyramid.registry import Registry
        registry = Registry()
        registry.introspector = DummyIntrospector()
        
        return registry

    def _makeIntrospectable(self, category, discrim, request_methods=None):
        from pyramid.registry import Introspectable
        intr = Introspectable(category, discrim, 'title', 'type')

        intr['request_methods'] = request_methods

        return intr

    def test_good_args(self):
        cmd = self._getTargetClass()([])
        cmd.bootstrap = (dummy.DummyBootstrap(),)
        cmd.args = ('/foo/bar/myapp.ini#myapp', 'a=1')
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        cmd._get_mapper = lambda *arg: mapper
        L = []
        cmd.out = lambda msg: L.append(msg)
        cmd.run()
        self.assertTrue('<unknown>' in ''.join(L))

    def test_bad_args(self):
        cmd = self._getTargetClass()([])
        cmd.bootstrap = (dummy.DummyBootstrap(),)
        cmd.args = ('/foo/bar/myapp.ini#myapp', 'a')
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        cmd._get_mapper = lambda *arg: mapper

        self.assertRaises(ValueError, cmd.run)

    def test_no_routes(self):
        command = self._makeOne()
        mapper = dummy.DummyMapper()
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(L, [])

    def test_no_mapper(self):
        command = self._makeOne()
        command._get_mapper = lambda *arg:None
        L = []
        command.out = L.append
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(L, [])

    def test_single_route_no_route_registered(self):
        command = self._makeOne()
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        registry = self._makeRegistry()
        command.bootstrap = (dummy.DummyBootstrap(registry=registry),)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(L), 3)
        self.assertEqual(L[-1].split(), ['a', '/a', '<unknown>', '<unknown>'])

    def test_route_with_no_slash_prefix(self):
        command = self._makeOne()
        route = dummy.DummyRoute('a', 'a')
        mapper = dummy.DummyMapper(route)
        registry = self._makeRegistry()
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        command.bootstrap = (dummy.DummyBootstrap(registry=registry),)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(L), 3)
        self.assertEqual(L[-1].split(), ['a', '/a', '<unknown>', '<unknown>'])


    def test_single_route_no_views_registered(self):
        from zope.interface import Interface
        from pyramid.interfaces import IRouteRequest
        registry = self._makeRegistry()
        registry.introspector.add(self._makeIntrospectable('routes', 'a'))

        def view():pass
        class IMyRoute(Interface):
            pass
        registry.registerUtility(IMyRoute, IRouteRequest, name='a')
        command = self._makeOne()
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        command.bootstrap = (dummy.DummyBootstrap(registry=registry),)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(L), 3)
        self.assertEqual(L[-1].split()[:3], ['a', '/a', 'None'])
                                                                                

    def test_single_route_one_view_registered(self):
        from zope.interface import Interface
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView

        registry = self._makeRegistry()
        def view():pass
        class IMyRoute(Interface):
            pass
        registry.registerAdapter(view,
                                 (IViewClassifier, IMyRoute, Interface),
                                 IView, '')
        registry.registerUtility(IMyRoute, IRouteRequest, name='a')
        registry.introspector.add(self._makeIntrospectable('routes', 'a'))
        command = self._makeOne()
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        command.bootstrap = (dummy.DummyBootstrap(registry=registry),)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(L), 3)
        compare_to = L[-1].split()[:3]
        self.assertEqual(compare_to, ['a', '/a', 'pyramid.tests.test_scripts.test_proutes.view'])
        
    def test_single_route_one_view_registered_with_factory(self):
        from zope.interface import Interface
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView

        registry = self._makeRegistry()

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
        route = dummy.DummyRoute('a', '/a', factory=factory)
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        L = []
        command.out = L.append
        command.bootstrap = (dummy.DummyBootstrap(registry=registry),)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(L), 3)
        self.assertEqual(L[-1].split()[:3], ['a', '/a', '<unknown>'])

    def test__get_mapper(self):
        from pyramid.registry import Registry
        from pyramid.urldispatch import RoutesMapper
        command = self._makeOne()
        registry = Registry()
        result = command._get_mapper(registry)
        self.assertEqual(result.__class__, RoutesMapper)
        
class Test_main(unittest.TestCase):
    def _callFUT(self, argv):
        from pyramid.scripts.proutes import main
        return main(argv, quiet=True)

    def test_it(self):
        result = self._callFUT(['proutes'])
        self.assertEqual(result, 2)

