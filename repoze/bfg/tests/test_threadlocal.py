from repoze.bfg.testing import cleanUp
import unittest

class TestThreadLocalManager(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.threadlocal import ThreadLocalManager
        return ThreadLocalManager

    def _makeOne(self, default=lambda *x: 1):
        return self._getTargetClass()(default)

    def test_init(self):
        local = self._makeOne()
        self.assertEqual(local.stack, [])
        self.assertEqual(local.get(), 1)

    def test_default(self):
        from zope.component import getGlobalSiteManager
        local = self._makeOne(getGlobalSiteManager)
        self.assertEqual(local.stack, [])
        self.assertEqual(local.get(), getGlobalSiteManager())

    def test_push_and_pop(self):
        local = self._makeOne()
        local.push(True)
        self.assertEqual(local.get(), True)
        self.assertEqual(local.pop(), True)
        self.assertEqual(local.pop(), None)
        self.assertEqual(local.get(), 1)

    def test_set_get_and_clear(self):
        local = self._makeOne()
        local.set(None)
        self.assertEqual(local.stack, [None])
        self.assertEqual(local.get(), None)
        local.clear()
        self.assertEqual(local.get(), 1)
        local.clear()
        self.assertEqual(local.get(), 1)

