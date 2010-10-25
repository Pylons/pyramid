import unittest

class NewRequestEventTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.events import NewRequest
        return NewRequest

    def _makeOne(self, request):
        return self._getTargetClass()(request)

    def test_class_implements(self):
        from repoze.bfg.interfaces import INewRequest
        from zope.interface.verify import verifyClass
        klass = self._getTargetClass()
        verifyClass(INewRequest, klass)
        
    def test_instance_implements(self):
        from repoze.bfg.interfaces import INewRequest
        from zope.interface.verify import verifyObject
        request = DummyRequest()
        inst = self._makeOne(request)
        verifyObject(INewRequest, inst)

    def test_ctor(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        self.assertEqual(inst.request, request)

class NewResponseEventTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.events import NewResponse
        return NewResponse

    def _makeOne(self, request, response):
        return self._getTargetClass()(request, response)

    def test_class_implements(self):
        from repoze.bfg.interfaces import INewResponse
        from zope.interface.verify import verifyClass
        klass = self._getTargetClass()
        verifyClass(INewResponse, klass)
        
    def test_instance_implements(self):
        from repoze.bfg.interfaces import INewResponse
        from zope.interface.verify import verifyObject
        request = DummyRequest()
        response = DummyResponse()
        inst = self._makeOne(request, response)
        verifyObject(INewResponse, inst)

    def test_ctor(self):
        request = DummyRequest()
        response = DummyResponse()
        inst = self._makeOne(request, response)
        self.assertEqual(inst.request, request)
        self.assertEqual(inst.response, response)

class ApplicationCreatedEventTests(unittest.TestCase):
    def test_alias_object_implements(self):
        from repoze.bfg.events import WSGIApplicationCreatedEvent
        event = WSGIApplicationCreatedEvent(object())
        from repoze.bfg.interfaces import IWSGIApplicationCreatedEvent
        from repoze.bfg.interfaces import IApplicationCreated
        from zope.interface.verify import verifyObject
        verifyObject(IWSGIApplicationCreatedEvent, event)
        verifyObject(IApplicationCreated, event)

    def test_alias_class_implements(self):
        from repoze.bfg.events import WSGIApplicationCreatedEvent
        from repoze.bfg.interfaces import IWSGIApplicationCreatedEvent
        from repoze.bfg.interfaces import IApplicationCreated
        from zope.interface.verify import verifyClass
        verifyClass(IWSGIApplicationCreatedEvent, WSGIApplicationCreatedEvent)
        verifyClass(IApplicationCreated, WSGIApplicationCreatedEvent)

    def test_object_implements(self):
        from repoze.bfg.events import ApplicationCreated
        event = ApplicationCreated(object())
        from repoze.bfg.interfaces import IApplicationCreated
        from zope.interface.verify import verifyObject
        verifyObject(IApplicationCreated, event)

    def test_class_implements(self):
        from repoze.bfg.events import ApplicationCreated
        from repoze.bfg.interfaces import IApplicationCreated
        from zope.interface.verify import verifyClass
        verifyClass(IApplicationCreated, ApplicationCreated)

class ContextFoundEventTests(unittest.TestCase):
    def test_alias_class_implements(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.events import AfterTraversal
        from repoze.bfg.interfaces import IAfterTraversal
        from repoze.bfg.interfaces import IContextFound
        verifyClass(IAfterTraversal, AfterTraversal)
        verifyClass(IContextFound, AfterTraversal)
        
    def test_alias_instance_implements(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.events import AfterTraversal
        from repoze.bfg.interfaces import IAfterTraversal
        from repoze.bfg.interfaces import IContextFound
        request = DummyRequest()
        inst = AfterTraversal(request)
        verifyObject(IAfterTraversal, inst)
        verifyObject(IContextFound, inst)

    def test_class_implements(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.events import ContextFound
        from repoze.bfg.interfaces import IContextFound
        verifyClass(IContextFound, ContextFound)
        
    def test_instance_implements(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.events import ContextFound
        from repoze.bfg.interfaces import IContextFound
        request = DummyRequest()
        inst = ContextFound(request)
        verifyObject(IContextFound, inst)

class TestSubscriber(unittest.TestCase):
    def setUp(self):
        registry = DummyRegistry()
        from repoze.bfg.configuration import Configurator
        self.config = Configurator(registry)
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def _makeOne(self, *ifaces):
        from repoze.bfg.events import subscriber
        return subscriber(*ifaces)

    def test_register(self):
        from zope.interface import Interface
        class IFoo(Interface): pass
        class IBar(Interface): pass
        dec = self._makeOne(IFoo, IBar)
        def foo(): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.subscribed, [(foo, (IFoo, IBar))])

    def test___call__(self):
        dec = self._makeOne()
        dummy_venusian = DummyVenusian()
        dec.venusian = dummy_venusian
        def foo(): pass
        dec(foo)
        self.assertEqual(dummy_venusian.attached, [(foo, dec.register, 'bfg')])

class DummyConfigurator(object):
    def __init__(self):
        self.subscribed = []

    def add_subscriber(self, wrapped, ifaces):
        self.subscribed.append((wrapped, ifaces))

class DummyRegistry(object):
    pass
        
class DummyVenusian(object):
    def __init__(self):
        self.attached = []

    def attach(self, wrapped, fn, category=None):
        self.attached.append((wrapped, fn, category))

class Dummy:
    pass
        
class DummyRequest:
    pass

class DummyResponse:
    pass

