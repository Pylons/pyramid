import unittest

from pyramid.tests.test_config import IDummy

class AdaptersConfiguratorMixinTests(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.config import Configurator
        config = Configurator(*arg, **kw)
        return config

    def test_add_subscriber_defaults(self):
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            implements(IEvent)
        L = []
        def subscriber(event):
            L.append(event)
        config = self._makeOne(autocommit=True)
        config.add_subscriber(subscriber)
        event = Event()
        config.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.notify(object())
        self.assertEqual(len(L), 2)

    def test_add_subscriber_iface_specified(self):
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            implements(IEvent)
        L = []
        def subscriber(event):
            L.append(event)
        config = self._makeOne(autocommit=True)
        config.add_subscriber(subscriber, IEvent)
        event = Event()
        config.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.notify(object())
        self.assertEqual(len(L), 1)

    def test_add_subscriber_dottednames(self):
        import pyramid.tests.test_config
        from pyramid.interfaces import INewRequest
        config = self._makeOne(autocommit=True)
        config.add_subscriber('pyramid.tests.test_config',
                              'pyramid.interfaces.INewRequest')
        handlers = list(config.registry.registeredHandlers())
        self.assertEqual(len(handlers), 1)
        handler = handlers[0]
        self.assertEqual(handler.handler, pyramid.tests.test_config)
        self.assertEqual(handler.required, (INewRequest,))

    def test_add_object_event_subscriber(self):
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            object = 'foo'
            implements(IEvent)
        event = Event()
        L = []
        def subscriber(object, event):
            L.append(event)
        config = self._makeOne(autocommit=True)
        config.add_subscriber(subscriber, (Interface, IEvent))
        config.registry.subscribers((event.object, event), None)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.subscribers((event.object, IDummy), None)
        self.assertEqual(len(L), 1)

    def test_add_response_adapter(self):
        from pyramid.interfaces import IResponse
        config = self._makeOne(autocommit=True)
        class Adapter(object):
            def __init__(self, other):
                self.other = other
        config.add_response_adapter(Adapter, str)
        result = config.registry.queryAdapter('foo', IResponse)
        self.assertTrue(result.other, 'foo')

    def test_add_response_adapter_self(self):
        from pyramid.interfaces import IResponse
        config = self._makeOne(autocommit=True)
        class Adapter(object):
            pass
        config.add_response_adapter(None, Adapter)
        adapter = Adapter()
        result = config.registry.queryAdapter(adapter, IResponse)
        self.assertTrue(result is adapter)

    def test_add_response_adapter_dottednames(self):
        from pyramid.interfaces import IResponse
        config = self._makeOne(autocommit=True)
        config.add_response_adapter('pyramid.response.Response',
                                    'types.StringType')
        result = config.registry.queryAdapter('foo', IResponse)
        self.assertTrue(result.body, 'foo')

