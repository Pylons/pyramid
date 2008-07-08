import unittest

from zope.component.testing import PlacelessSetup

class RouterTests(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _registerTraverserFactory(self, app, name, *for_):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import IPublishTraverserFactory
        gsm.registerAdapter(app, for_, IPublishTraverserFactory, name)

    def _registerViewFactory(self, app, name, *for_):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import IViewFactory
        gsm.registerAdapter(app, for_, IViewFactory, name)

    def _registerWSGIFactory(self, app, name, *for_):
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

    def test_call_no_view_registered(self):
        rootpolicy = make_rootpolicy(None)
        environ = self._makeEnviron()
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        self._registerTraverserFactory(traversalfactory, '', None, None)
        router = self._makeOne(rootpolicy)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless('http://localhost:8080' in result[0], result)

    def test_call_default_view_redirect(self):
        rootpolicy = make_rootpolicy(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        response = DummyResponse()
        viewfactory = make_view_factory(response)
        wsgifactory = make_wsgi_factory('200 OK', (), ['Hello world'])
        environ = self._makeEnviron(PATH_INFO='/doesnt/end/in/slash')
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerViewFactory(viewfactory, '', None, None)
        self._registerWSGIFactory(wsgifactory, '', None, None)
        router = self._makeOne(rootpolicy)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 3)
        self.assertEqual(
            headers[0],
            ('content-type', 'text/html; charset=UTF-8'))
        self.assertEqual(
            headers[1],
            ('location', 'http://localhost:8080/doesnt/end/in/slash/'))
        self.assertEqual(start_response.status, '302 Found')

    def test_call_view_registered_nonspecific_default_path(self):
        rootpolicy = make_rootpolicy(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        response = DummyResponse()
        viewfactory = make_view_factory(response)
        wsgifactory = make_wsgi_factory('200 OK', (), ['Hello world'])
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerViewFactory(viewfactory, '', None, None)
        self._registerWSGIFactory(wsgifactory, '', None, None)
        router = self._makeOne(rootpolicy)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        request = environ['request']
        self.assertEqual(environ['request'].subpath, [])
        self.assertEqual(environ['view'].context, context)

    def test_call_view_registered_nonspecific_nondefault_path_and_subpath(self):
        rootpolicy = make_rootpolicy(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, 'foo', ['bar'])
        response = DummyResponse()
        viewfactory = make_view_factory(response)
        wsgifactory = make_wsgi_factory('200 OK', (), ['Hello world'])
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerViewFactory(viewfactory, 'foo', None, None)
        self._registerWSGIFactory(wsgifactory, '', None, None)
        router = self._makeOne(rootpolicy)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        request = environ['request']
        self.assertEqual(environ['request'].subpath, ['bar'])
        self.assertEqual(environ['view'].context, context)

    def test_call_view_registered_specific_success(self):
        rootpolicy = make_rootpolicy(None)
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        traversalfactory = make_traversal_factory(context, '', [])
        response = DummyResponse()
        viewfactory = make_view_factory(response)
        wsgifactory = make_wsgi_factory('200 OK', (), ['Hello world'])
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerViewFactory(viewfactory, '', IContext, IRequest)
        self._registerWSGIFactory(wsgifactory, '', None, None)
        router = self._makeOne(rootpolicy)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        request = environ['request']
        self.assertEqual(environ['request'].subpath, [])
        self.assertEqual(environ['view'].context, context)

    def test_call_view_registered_specific_fail(self):
        rootpolicy = make_rootpolicy(None)
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        class INotContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, INotContext)
        traversalfactory = make_traversal_factory(context, '', [''])
        response = DummyResponse()
        viewfactory = make_view_factory(response)
        wsgifactory = make_wsgi_factory('200 OK', (), ['Hello world'])
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerViewFactory(viewfactory, '', IContext, IRequest)
        self._registerWSGIFactory(wsgifactory, '', None, None)
        router = self._makeOne(rootpolicy)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.failUnless('404' in result[0])
        self.assertEqual(start_response.status, '404 Not Found')

class DummyContext:
    pass

def make_wsgi_factory(status, headers, app_iter):
    class DummyWSGIApplicationFactory:
        def __init__(self, view, request):
            self.view = view
            self.request = request

        def __call__(self, environ, start_response):
            environ['view'] = self.view
            environ['request'] = self.request
            start_response(status, headers)
            return app_iter

    return DummyWSGIApplicationFactory

def make_view_factory(response):
    class DummyViewFactory:
        def __init__(self, context, request):
            self.context = context
            self.request = request

        def __call__(self):
            return response
    return DummyViewFactory

def make_traversal_factory(context, name, subpath):
    class DummyTraversalFactory:
        def __init__(self, root, request):
            self.root = root
            self.request = request

        def __call__(self, path):
            return context, name, subpath
    return DummyTraversalFactory

def make_rootpolicy(root):
    def rootpolicy(environ):
        return root
    return rootpolicy

class DummyStartResponse:
    status = ()
    headers = ()
    def __call__(self, status, headers):
        self.status = status
        self.headers = headers
        
class DummyResponse:
    status = '200 OK'
    headerlist = ()
    app_iter = ()
    
