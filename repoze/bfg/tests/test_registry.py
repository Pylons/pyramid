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
