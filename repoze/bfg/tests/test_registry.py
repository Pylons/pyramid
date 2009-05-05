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

class TestPopulateRegistry(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.registry import populateRegistry
        return populateRegistry(*arg, **kw)

    def test_it(self):
        from repoze.bfg.tests import fixtureapp
        dummylock = DummyLock()
        dummyregmgr = DummyRegistrationManager()
        import repoze.bfg.registry
        try:
            old = repoze.bfg.registry.setRegistryManager(dummyregmgr)
            from zope.component.registry import Components
            registry = Components('hello')
            self._callFUT(registry,
                          'configure.zcml',
                          fixtureapp,
                          lock=dummylock)
            self.assertEqual(dummylock.acquired, True)
            self.assertEqual(dummylock.released, True)
            self.assertEqual(dummyregmgr.registry, registry)
        finally:
            repoze.bfg.registry.setRegistryManager(old)

class TestThreadLocalRegistryManager(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.registry import ThreadLocalRegistryManager
        return ThreadLocalRegistryManager

    def _makeOne(self):
        return self._getTargetClass()()

    def test_init(self):
        local = self._makeOne()
        from zope.component import getGlobalSiteManager
        self.assertEqual(local.stack, [])
        self.assertEqual(local.get(), getGlobalSiteManager())

    def test_push_and_pop(self):
        local = self._makeOne()
        from zope.component import getGlobalSiteManager
        local.push(True)
        self.assertEqual(local.get(), True)
        self.assertEqual(local.pop(), True)
        self.assertEqual(local.pop(), None)
        self.assertEqual(local.get(), getGlobalSiteManager())

    def test_set_get_and_clear(self):
        local = self._makeOne()
        from zope.component import getGlobalSiteManager
        local.set(None)
        self.assertEqual(local.stack, [None])
        self.assertEqual(local.get(), None)
        local.clear()
        self.assertEqual(local.get(), getGlobalSiteManager())
        local.clear()
        self.assertEqual(local.get(), getGlobalSiteManager())

class GetSiteManagerTests(unittest.TestCase):
    def _callFUT(self, context=None):
        from repoze.bfg.registry import getSiteManager
        return getSiteManager(context)

    def test_no_context(self):
        from zope.component import getGlobalSiteManager
        self.assertEqual(self._callFUT(), getGlobalSiteManager())
    
    def test_with_context(self):
        from zope.component.interfaces import ComponentLookupError
        self.assertRaises(ComponentLookupError, self._callFUT, object)
        
class DummyRegistrationManager:
    def push(self, registry):
        self.registry = registry

    def pop(self):
        self.popped = True

    def get(self):
        return self.registry

class DummyLock:
    def acquire(self):
        self.acquired = True

    def release(self):
        self.released = True
        
