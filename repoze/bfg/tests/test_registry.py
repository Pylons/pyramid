import unittest

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

