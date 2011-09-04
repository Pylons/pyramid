import unittest

class TestRegistry(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.registry import Registry
        return Registry
    
    def _makeOne(self):
        return self._getTargetClass()()

    def test___nonzero__(self):
        registry = self._makeOne()
        self.assertEqual(registry.__nonzero__(), True)

    def test_registerHandler_and_notify(self):
        registry = self._makeOne()
        self.assertEqual(registry.has_listeners, False)
        L = []
        def f(event):
            L.append(event)
        registry.registerHandler(f, [IDummyEvent])
        self.assertEqual(registry.has_listeners, True)
        event = DummyEvent()
        registry.notify(event)
        self.assertEqual(L, [event])

    def test_registerSubscriptionAdapter(self):
        registry = self._makeOne()
        self.assertEqual(registry.has_listeners, False)
        from zope.interface import Interface
        registry.registerSubscriptionAdapter(DummyEvent,
                                             [IDummyEvent], Interface)
        self.assertEqual(registry.has_listeners, True)

    def test__get_settings(self):
        registry = self._makeOne()
        registry._settings = 'foo'
        self.assertEqual(registry.settings, 'foo')

    def test__set_settings(self):
        registry = self._makeOne()
        registry.settings = 'foo'
        self.assertEqual(registry._settings, 'foo')

class DummyModule:
    __path__ = "foo"
    __name__ = "dummy"
    __file__ = ''

from zope.interface import Interface
from zope.interface import implements
class IDummyEvent(Interface):
    pass

class DummyEvent(object):
    implements(IDummyEvent)
