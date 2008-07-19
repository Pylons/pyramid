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
        from repoze.bfg.interfaces import ITraverserFactory
        gsm.registerAdapter(app, for_, ITraverserFactory, name)

    def _registerView(self, app, name, *for_):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import IView
        gsm.registerAdapter(app, for_, IView, name)

    def _registerPermission(self, permission, name, *for_):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import IViewPermission
        gsm.registerAdapter(permission, for_, IViewPermission, name)

    def _registerSecurityPolicy(self, secpol):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import ISecurityPolicy
        gsm.registerUtility(secpol, ISecurityPolicy)

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
        router = self._makeOne(rootpolicy, None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless('http://localhost:8080' in result[0], result)

    def test_call_view_registered_nonspecific_default_path(self):
        rootpolicy = make_rootpolicy(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerView(view, '', None, None)
        router = self._makeOne(rootpolicy, None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], '')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], [])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)

    def test_call_view_registered_nonspecific_nondefault_path_and_subpath(self):
        rootpolicy = make_rootpolicy(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, 'foo', ['bar'])
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerView(view, 'foo', None, None)
        router = self._makeOne(rootpolicy, None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], 'foo')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], ['bar'])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)

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
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne(rootpolicy, None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], '')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], [])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)

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
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerView(view, '', IContext, IRequest)
        app_context = make_appcontext()
        router = self._makeOne(rootpolicy, None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '404 Not Found')
        self.failUnless('404' in result[0])

    def test_call_view_registered_security_policy_permission_none(self):
        rootpolicy = make_rootpolicy(None)
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        traversalfactory = make_traversal_factory(context, '', [''])
        response = DummyResponse()
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerView(view, '', IContext, IRequest)
        secpol = DummySecurityPolicy()
        self._registerSecurityPolicy(secpol)
        app_context = make_appcontext()
        router = self._makeOne(rootpolicy, None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '200 OK')

    def test_call_view_registered_security_policy_permission_succeeds(self):
        rootpolicy = make_rootpolicy(None)
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        traversalfactory = make_traversal_factory(context, '', [''])
        response = DummyResponse()
        view = make_view(response)
        secpol = DummySecurityPolicy()
        permissionfactory = make_permission_factory(True)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerView(view, '', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, '', IContext, IRequest)
        app_context = make_appcontext()
        router = self._makeOne(rootpolicy, None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(permissionfactory.checked_with, secpol)

    def test_call_view_registered_security_policy_permission_fails(self):
        rootpolicy = make_rootpolicy(None)
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        traversalfactory = make_traversal_factory(context, '', [''])
        response = DummyResponse()
        view = make_view(response)
        secpol = DummySecurityPolicy()
        permissionfactory = make_permission_factory(False)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None, None)
        self._registerView(view, '', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, '', IContext, IRequest)
        app_context = make_appcontext()
        router = self._makeOne(rootpolicy, None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '401 Unauthorized')
        self.failUnless('permission' in result[0])
        self.assertEqual(permissionfactory.checked_with, secpol)

class MakeAppTests(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.router import make_app
        return make_app

    def test_sampleapp(self):
        from repoze.bfg.tests import fixtureapp
        make_app = self._getFUT()
        rootpolicy = make_rootpolicy(None)
        app = make_app(rootpolicy, fixtureapp)
        self.assertEqual(app.registry.__name__, 'repoze.bfg.tests.fixtureapp')
        self.assertEqual(app.root_policy, rootpolicy)

class DummyContext:
    pass

def make_wsgi_factory(status, headers, app_iter):
    class DummyWSGIApplicationFactory:
        def __init__(self, context, request, view):
            self.context = context
            self.request = request
            self.view = view

        def __call__(self, environ, start_response):
            environ['context'] = self.context
            environ['request'] = self.request
            environ['view'] = self.view
            start_response(status, headers)
            return app_iter

    return DummyWSGIApplicationFactory

def make_view(response):
    def view(context, request):
        return response
    return view

def make_traversal_factory(context, name, subpath):
    class DummyTraversalFactory:
        def __init__(self, root, request):
            self.root = root
            self.request = request

        def __call__(self, path):
            return context, name, subpath
    return DummyTraversalFactory

def make_permission_factory(result):
    class DummyPermissionFactory:
        def __init__(self, context, request):
            self.context = context
            self.request = request

        def __call__(self, secpol):
            self.__class__.checked_with = secpol
            return result

        def __repr__(self):
            return 'permission'
    return DummyPermissionFactory

def make_rootpolicy(root):
    def rootpolicy(environ):
        return root
    return rootpolicy

def make_appcontext():
    from zope.configuration.interfaces import IConfigurationContext
    from zope.interface import directlyProvides
    app_context = DummyContext()
    directlyProvides(app_context, IConfigurationContext)
    return app_context

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
    
class DummySecurityPolicy:
    pass

