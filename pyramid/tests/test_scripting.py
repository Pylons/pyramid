import unittest

class Test_get_root(unittest.TestCase):
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

class Test_prepare(unittest.TestCase):
    def _callFUT(self, request=None, registry=None):
        from pyramid.scripting import prepare
        return prepare(request, registry)

    def _makeRegistry(self):
        return DummyRegistry(DummyFactory)

    def setUp(self):
        from pyramid.threadlocal import manager
        self.manager = manager
        self.default = manager.get()

    def test_it_no_valid_apps(self):
        from pyramid.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError, self._callFUT)

    def test_it_norequest(self):
        registry = self._makeRegistry()
        info = self._callFUT(registry=registry)
        root, closer = info['root'], info['closer']
        pushed = self.manager.get()
        self.assertEqual(pushed['registry'], registry)
        self.assertEqual(pushed['request'].registry, registry)
        self.assertEqual(root.a, (pushed['request'],))
        closer()
        self.assertEqual(self.default, self.manager.get())

    def test_it_withrequest(self):
        request = DummyRequest({})
        registry = request.registry = self._makeRegistry()
        info = self._callFUT(request=request)
        root, closer = info['root'], info['closer']
        pushed = self.manager.get()
        self.assertEqual(pushed['request'], request)
        self.assertEqual(pushed['registry'], registry)
        self.assertEqual(pushed['request'].registry, registry)
        self.assertEqual(root.a, (request,))
        closer()
        self.assertEqual(self.default, self.manager.get())

    def test_it_with_request_and_registry(self):
        request = DummyRequest({})
        registry = request.registry = self._makeRegistry()
        info = self._callFUT(request=request, registry=registry)
        root, closer = info['root'], info['closer']
        pushed = self.manager.get()
        self.assertEqual(pushed['request'], request)
        self.assertEqual(pushed['registry'], registry)
        self.assertEqual(pushed['request'].registry, registry)
        self.assertEqual(root.a, (request,))
        closer()
        self.assertEqual(self.default, self.manager.get())

class Test__make_request(unittest.TestCase):
    def _callFUT(self, path='/', registry=None):
        from pyramid.scripting import _make_request
        return _make_request(path, registry)

    def test_it_with_registry(self):
        request = self._callFUT('/', dummy_registry)
        self.assertEqual(request.environ['path'], '/')
        self.assertEqual(request.registry, dummy_registry)

    def test_it_with_no_registry(self):
        from pyramid.config import global_registries
        # keep registry local so that global_registries is cleared after
        registry = DummyRegistry(DummyFactory)
        global_registries.add(registry)
        try:
            request = self._callFUT('/hello')
            self.assertEqual(request.environ['path'], '/hello')
            self.assertEqual(request.registry, registry)
        finally:
            global_registries.empty()

class Dummy:
    pass

dummy_root = Dummy()

class DummyFactory(object):
    @classmethod
    def blank(cls, path):
        req = DummyRequest({'path': path})
        return req

    def __init__(self, *a, **kw):
        self.a = a
        self.kw = kw

class DummyRegistry(object):
    def __init__(self, factory=None):
        self.factory = factory

    def queryUtility(self, iface, default=None):
        return self.factory or default

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
        
