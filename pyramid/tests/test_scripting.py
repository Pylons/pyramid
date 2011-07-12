import unittest

class TestGetRoot(unittest.TestCase):
    def _callFUT(self, app, request=None):
        from pyramid.scripting import get_root
        return get_root(app, request)

    def test_it_norequest(self):
        app = DummyApp(registry=dummy_registry)
        root, closer = self._callFUT(app)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['registry'], dummy_registry)
        self.assertEqual(pushed['request'].registry, app.registry)
        self.assertEqual(len(app.threadlocal_manager.popped), 0)
        closer()
        self.assertEqual(len(app.threadlocal_manager.popped), 1)

    def test_it_withrequest(self):
        app = DummyApp(registry=dummy_registry)
        request = DummyRequest({})
        root, closer = self._callFUT(app, request)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['registry'], dummy_registry)
        self.assertEqual(pushed['request'], request)
        self.assertEqual(len(app.threadlocal_manager.popped), 0)
        closer()
        self.assertEqual(len(app.threadlocal_manager.popped), 1)

    def test_it_requestfactory_overridden(self):
        app = DummyApp(registry=dummy_registry)
        root, closer = self._callFUT(app)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['request'].environ['path'], '/')

class TestMakeRequest(unittest.TestCase):
    def _callFUT(self, path='/', registry=None):
        from pyramid.scripting import make_request
        return make_request(path, registry)

    def test_it_with_registry(self):
        request = self._callFUT('/', dummy_registry)
        self.assertEqual(request.environ['path'], '/')
        self.assertEqual(request.registry, dummy_registry)

    def test_it_with_no_registry(self):
        from pyramid.config import global_registries
        # keep registry local so that global_registries is cleared after
        registry = DummyRegistry(DummyFactory)
        global_registries.add(registry)
        request = self._callFUT('/hello')
        self.assertEqual(request.environ['path'], '/hello')
        self.assertEqual(request.registry, registry)

class Dummy:
    pass

dummy_root = Dummy()

class DummyFactory(object):
    @classmethod
    def blank(cls, path):
        req = DummyRequest({'path': path})
        return req

class DummyRegistry(object):
    def __init__(self, result=None):
        self.result = result

    def queryUtility(self, iface, default=None):
        return self.result or default

dummy_registry = DummyRegistry(DummyFactory)

class DummyApp:
    def __init__(self, registry=None):
        self.threadlocal_manager = DummyThreadLocalManager()
        if registry:
            self.registry = registry

    def root_factory(self, environ):
        return dummy_root

class DummyThreadLocalManager:
    def __init__(self):
        self.pushed = []
        self.popped = []
        
    def push(self, item):
        self.pushed.append(item)

    def pop(self):
        self.popped.append(True)
        
class DummyRequest:
    def __init__(self, environ):
        self.environ = environ
        
