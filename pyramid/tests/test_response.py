import unittest
from pyramid import testing

class TestResponse(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.response import Response
        return Response
        
    def test_implements_IResponse(self):
        from pyramid.interfaces import IResponse
        cls = self._getTargetClass()
        self.assertTrue(IResponse.implementedBy(cls))

    def test_provides_IResponse(self):
        from pyramid.interfaces import IResponse
        inst = self._getTargetClass()()
        self.assertTrue(IResponse.providedBy(inst))

class Dummy(object):
    pass

class DummyConfigurator(object):
    def __init__(self):
        self.adapters = []

    def add_response_adapter(self, wrapped, type_or_iface):
        self.adapters.append((wrapped, type_or_iface))

class DummyVenusian(object):
    def __init__(self):
        self.attached = []

    def attach(self, wrapped, fn, category=None):
        self.attached.append((wrapped, fn, category))

class TestResponseAdapter(unittest.TestCase):
    def setUp(self):
        registry = Dummy()
        self.config = testing.setUp(registry=registry)

    def tearDown(self):
        self.config.end()

    def _makeOne(self, *types_or_ifaces):
        from pyramid.response import response_adapter
        return response_adapter(*types_or_ifaces)

    def test_register_single(self):
        from zope.interface import Interface
        class IFoo(Interface): pass
        dec = self._makeOne(IFoo)
        def foo(): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.adapters, [(foo, IFoo)])

    def test_register_multi(self):
        from zope.interface import Interface
        class IFoo(Interface): pass
        class IBar(Interface): pass
        dec = self._makeOne(IFoo, IBar)
        def foo(): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.adapters, [(foo, IFoo), (foo, IBar)])

    def test___call__(self):
        from zope.interface import Interface
        class IFoo(Interface): pass
        dec = self._makeOne(IFoo)
        dummy_venusian = DummyVenusian()
        dec.venusian = dummy_venusian
        def foo(): pass
        dec(foo)
        self.assertEqual(dummy_venusian.attached,
                         [(foo, dec.register, 'pyramid')])
