import unittest

class TestGetRoot(unittest.TestCase):
    def _callFUT(self, router):
        from repoze.bfg.scripting import get_root
        return get_root(router)

    def test_it(self):
        router = DummyRouter()
        result = self._callFUT(router)
        self.assertEqual(result, router)
        self.assertEqual(len(router.threadlocal_manager.pushed), 1)
        self.assertEqual(router.threadlocal_manager.pushed[0],
                         {'registry':None, 'request':None})
        

class DummyThreadLocalManager:
    def __init__(self):
        self.pushed = []

    def push(self, val):
        self.pushed.append(val)

class DummyRouter:
    def __init__(self):
        self.registry = None
        self.threadlocal_manager = DummyThreadLocalManager()

    def root_factory(self, environ):
        return self
    
