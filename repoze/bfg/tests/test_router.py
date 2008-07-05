import unittest

from zope.component.testing import PlacelessSetup

class RouterTests(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _registerFactory(self, app, name, *for_):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import IWSGIApplicationFactory
        gsm.registerAdapter(app, for_, IWSGIApplicationFactory, name)
        
    def _getTargetClass(self):
        from repoze.bfg.router import Router
        return Router

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def _makeEnviron(self, **extras):
        environ = {
            'wsgi.url_scheme':'http',
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'8080',
            'REQUEST_METHOD':'GET',
            }
        environ.update(extras)
        return environ

    def test_call_no_app_registered(self):
        statii = []
        headerii = []
        def rootpolicy(environ):
            return None
        def traversalpolicy(root, environ):
            return DummyContext(), 'foo', []
        def start_response(status, headers):
            statii[:] = [status]
            headerii[:] = [headers]
        environ = self._makeEnviron()
        router = self._makeOne(rootpolicy, traversalpolicy)
        result = router(environ, start_response)
        headers = headerii[0]
        self.assertEqual(len(headers), 2)
        status = statii[0]
        self.assertEqual(status, '404 Not Found')
        self.failUnless('http://localhost:8080' in result[0], result)

    def test_call_app_registered_nonspecific_default_path(self):
        def rootpolicy(environ):
            return None
        context = DummyContext()
        def traversalpolicy(root, environ):
            return context, '', []
        def start_response(status, headers):
            pass
        environ = self._makeEnviron()
        self._registerFactory(DummyWSGIApplicationFactory, '', None, None)
        router = self._makeOne(rootpolicy, traversalpolicy)
        result = router(environ, start_response)
        self.failUnless(result[0] is context)
        import webob
        self.failUnless(isinstance(result[1], webob.Request))
        self.assertEqual(environ['repoze.bfg.subpath'], [])

    def test_call_app_registered_nonspecific_nondefault_path_and_subpath(self):
        def rootpolicy(environ):
            return None
        context = DummyContext()
        def traversalpolicy(root, environ):
            return context, 'foo', ['bar', 'baz']
        def start_response(status, headers):
            pass
        environ = self._makeEnviron()
        self._registerFactory(DummyWSGIApplicationFactory, 'foo', None, None)
        router = self._makeOne(rootpolicy, traversalpolicy)
        result = router(environ, start_response)
        self.failUnless(result[0] is context)
        import webob
        self.failUnless(isinstance(result[1], webob.Request))
        self.assertEqual(environ['repoze.bfg.subpath'], ['bar', 'baz'])

    def test_call_app_registered_specific_success(self):
        def rootpolicy(environ):
            return None
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        def traversalpolicy(root, environ):
            return context, 'foo', ['bar', 'baz']
        def start_response(status, headers):
            pass
        environ = self._makeEnviron()
        from repoze.bfg.interfaces import IWebObRequest
        self._registerFactory(DummyWSGIApplicationFactory, 'foo', IContext,
                              IWebObRequest)
        router = self._makeOne(rootpolicy, traversalpolicy)
        result = router(environ, start_response)
        self.failUnless(result[0] is context)
        import webob
        self.failUnless(isinstance(result[1], webob.Request))
        self.assertEqual(environ['repoze.bfg.subpath'], ['bar', 'baz'])

    def test_call_app_registered_specific_fail(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class INotContext(Interface):
            pass
        class IContext(Interface):
            pass
        directlyProvides(context, INotContext)
        statii = []
        headerii = []
        def rootpolicy(environ):
            return None
        def traversalpolicy(root, environ):
            return context, 'foo', []
        def start_response(status, headers):
            statii[:] = [status]
            headerii[:] = [headers]
        environ = self._makeEnviron()
        from repoze.bfg.interfaces import IWebObRequest
        self._registerFactory(DummyWSGIApplicationFactory, 'foo', IContext,
                              IWebObRequest)
        router = self._makeOne(rootpolicy, traversalpolicy)
        result = router(environ, start_response)
        headers = headerii[0]
        self.assertEqual(len(headers), 2)
        status = statii[0]
        self.assertEqual(status, '404 Not Found')
        self.failUnless('http://localhost:8080' in result[0], result)

class DummyContext:
    pass

class DummyWSGIApplicationFactory:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, environ, start_response):
        return self.context, self.request
