import unittest

from zope.component.testing import PlacelessSetup

class RouterTests(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _registerFactory(self, app, for_, name):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import IWSGIApplicationFactory
        gsm.registerAdapter(app, (for_,), IWSGIApplicationFactory, name)
        
    def _getTargetClass(self):
        from repoze.bfg.router import Router
        return Router

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_call_no_app_registered(self):
        def rootpolicy(environ):
            return None
        def traversalpolicy(root, environ):
            return DummyContext(), 'foo', []
        def start_response(status, headers):
            pass
        environ = {}
        router = self._makeOne(rootpolicy, traversalpolicy)
        from zope.component import ComponentLookupError
        self.assertRaises(ComponentLookupError, router, environ, start_response)

    def test_call_app_registered_default_path(self):
        def rootpolicy(environ):
            return None
        context = DummyContext()
        _marker = []
        def traversalpolicy(root, environ):
            return context, '', []
        def start_response(status, headers):
            pass
        class DummyWSGIApplicationFactory:
            def __init__(self, context):
                self.context = context

            def __call__(self, environ, start_response):
                return _marker
        environ = {}
        self._registerFactory(DummyWSGIApplicationFactory, None, '')
        router = self._makeOne(rootpolicy, traversalpolicy)
        result = router(environ, start_response)
        self.failUnless(result is _marker)
        self.assertEqual(environ['repoze.bfg.subpath'], [])

    def test_call_app_registered_nondefault_path_and_subpath(self):
        def rootpolicy(environ):
            return None
        context = DummyContext()
        _marker = []
        def traversalpolicy(root, environ):
            return context, 'foo', ['bar', 'baz']
        def start_response(status, headers):
            pass
        class DummyWSGIApplicationFactory:
            def __init__(self, context):
                self.context = context

            def __call__(self, environ, start_response):
                return _marker
        environ = {}
        self._registerFactory(DummyWSGIApplicationFactory, None, 'foo')
        router = self._makeOne(rootpolicy, traversalpolicy)
        result = router(environ, start_response)
        self.failUnless(result is _marker)
        self.assertEqual(environ['repoze.bfg.subpath'], ['bar', 'baz'])
        
class DummyContext:
    pass

    
