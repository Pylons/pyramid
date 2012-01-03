import unittest
from pyramid import testing

class NewRequestEventTests(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.events import NewRequest
        return NewRequest

    def _makeOne(self, request):
        return self._getTargetClass()(request)

    def test_class_implements(self):
        from pyramid.interfaces import INewRequest
        from zope.interface.verify import verifyClass
        klass = self._getTargetClass()
        verifyClass(INewRequest, klass)
        
    def test_instance_implements(self):
        from pyramid.interfaces import INewRequest
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
        from pyramid.events import NewResponse
        return NewResponse

    def _makeOne(self, request, response):
        return self._getTargetClass()(request, response)

    def test_class_implements(self):
        from pyramid.interfaces import INewResponse
        from zope.interface.verify import verifyClass
        klass = self._getTargetClass()
        verifyClass(INewResponse, klass)
        
    def test_instance_implements(self):
        from pyramid.interfaces import INewResponse
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
        from pyramid.events import WSGIApplicationCreatedEvent
        event = WSGIApplicationCreatedEvent(object())
        from pyramid.interfaces import IWSGIApplicationCreatedEvent
        from pyramid.interfaces import IApplicationCreated
        from zope.interface.verify import verifyObject
        verifyObject(IWSGIApplicationCreatedEvent, event)
        verifyObject(IApplicationCreated, event)

    def test_alias_class_implements(self):
        from pyramid.events import WSGIApplicationCreatedEvent
        from pyramid.interfaces import IWSGIApplicationCreatedEvent
        from pyramid.interfaces import IApplicationCreated
        from zope.interface.verify import verifyClass
        verifyClass(IWSGIApplicationCreatedEvent, WSGIApplicationCreatedEvent)
        verifyClass(IApplicationCreated, WSGIApplicationCreatedEvent)

    def test_object_implements(self):
        from pyramid.events import ApplicationCreated
        event = ApplicationCreated(object())
        from pyramid.interfaces import IApplicationCreated
        from zope.interface.verify import verifyObject
        verifyObject(IApplicationCreated, event)

    def test_class_implements(self):
        from pyramid.events import ApplicationCreated
        from pyramid.interfaces import IApplicationCreated
        from zope.interface.verify import verifyClass
        verifyClass(IApplicationCreated, ApplicationCreated)

class ContextFoundEventTests(unittest.TestCase):
    def test_alias_class_implements(self):
        from zope.interface.verify import verifyClass
        from pyramid.events import AfterTraversal
        from pyramid.interfaces import IAfterTraversal
        from pyramid.interfaces import IContextFound
        verifyClass(IAfterTraversal, AfterTraversal)
        verifyClass(IContextFound, AfterTraversal)
        
    def test_alias_instance_implements(self):
        from zope.interface.verify import verifyObject
        from pyramid.events import AfterTraversal
        from pyramid.interfaces import IAfterTraversal
        from pyramid.interfaces import IContextFound
        request = DummyRequest()
        inst = AfterTraversal(request)
        verifyObject(IAfterTraversal, inst)
        verifyObject(IContextFound, inst)

    def test_class_implements(self):
        from zope.interface.verify import verifyClass
        from pyramid.events import ContextFound
        from pyramid.interfaces import IContextFound
        verifyClass(IContextFound, ContextFound)
        
    def test_instance_implements(self):
        from zope.interface.verify import verifyObject
        from pyramid.events import ContextFound
        from pyramid.interfaces import IContextFound
        request = DummyRequest()
        inst = ContextFound(request)
        verifyObject(IContextFound, inst)

class TestSubscriber(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, *ifaces):
        from pyramid.events import subscriber
        return subscriber(*ifaces)

    def test_register_single(self):
        from zope.interface import Interface
        class IFoo(Interface): pass
        class IBar(Interface): pass
        dec = self._makeOne(IFoo)
        def foo(): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.subscribed, [(foo, IFoo)])

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
        self.assertEqual(config.subscribed, [(foo, IFoo), (foo, IBar)])

    def test_register_none_means_all(self):
        from zope.interface import Interface
        dec = self._makeOne()
        def foo(): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.subscribed, [(foo, Interface)])

    def test_register_objectevent(self):
        from zope.interface import Interface
        class IFoo(Interface): pass
        class IBar(Interface): pass
        dec = self._makeOne([IFoo, IBar])
        def foo(): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.subscribed, [(foo, [IFoo, IBar])])

    def test___call__(self):
        dec = self._makeOne()
        dummy_venusian = DummyVenusian()
        dec.venusian = dummy_venusian
        def foo(): pass
        dec(foo)
        self.assertEqual(dummy_venusian.attached,
                         [(foo, dec.register, 'pyramid')])

class TestBeforeRender(unittest.TestCase):
    def _makeOne(self, system, val=None):
        from pyramid.events import BeforeRender
        return BeforeRender(system, val)

    def test_instance_conforms(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IBeforeRender
        event = self._makeOne({})
        verifyObject(IBeforeRender, event)

    def test_setitem_success(self):
        event = self._makeOne({})
        event['a'] = 1
        self.assertEqual(event, {'a':1})

    def test_setdefault_fail(self):
        event = self._makeOne({})
        result = event.setdefault('a', 1)
        self.assertEqual(result, 1)
        self.assertEqual(event, {'a':1})
        
    def test_setdefault_success(self):
        event = self._makeOne({})
        event['a'] = 1
        result = event.setdefault('a', 2)
        self.assertEqual(result, 1)
        self.assertEqual(event, {'a':1})

    def test_update_success(self):
        event = self._makeOne({'a':1})
        event.update({'b':2})
        self.assertEqual(event, {'a':1, 'b':2})

    def test__contains__True(self):
        system = {'a':1}
        event = self._makeOne(system)
        self.assertTrue('a' in event)

    def test__contains__False(self):
        system = {}
        event = self._makeOne(system)
        self.assertFalse('a' in event)

    def test__getitem__success(self):
        system = {'a':1}
        event = self._makeOne(system)
        self.assertEqual(event['a'], 1)

    def test__getitem__fail(self):
        system = {}
        event = self._makeOne(system)
        self.assertRaises(KeyError, event.__getitem__, 'a')

    def test_get_success(self):
        system = {'a':1}
        event = self._makeOne(system)
        self.assertEqual(event.get('a'), 1)

    def test_get_fail(self):
        system = {}
        event = self._makeOne(system)
        self.assertEqual(event.get('a'), None)

    def test_rendering_val(self):
        system = {}
        val = {}
        event = self._makeOne(system, val)
        self.assertTrue(event.rendering_val is val)

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

