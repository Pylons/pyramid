import unittest

from zope.testing.cleanup import cleanUp

class RouterTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _registerLogger(self):
        from repoze.bfg.interfaces import ILogger
        class Logger:
            def __init__(self):
                self.messages = []
            def info(self, msg):
                self.messages.append(msg)
            debug = info
        logger = Logger()
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerUtility(logger, ILogger, name='repoze.bfg.debug')
        return logger

    def _registerSettings(self, **kw):
        from repoze.bfg.interfaces import ISettings
        class Settings:
            def __init__(self, **kw):
                self.__dict__.update(kw)

        defaultkw = {'debug_authorization':False, 'debug_notfound':False}
        defaultkw.update(kw)
        settings = Settings(**defaultkw)
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerUtility(settings, ISettings)

    def _registerTraverserFactory(self, app, name, *for_):
        from repoze.bfg.interfaces import ITraverserFactory
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(app, for_, ITraverserFactory, name)

    def _registerView(self, app, name, *for_):
        from repoze.bfg.interfaces import IView
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(app, for_, IView, name)

    def _registerPermission(self, permission, name, *for_):
        from repoze.bfg.interfaces import IViewPermission
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(permission, for_, IViewPermission, name)

    def _registerSecurityPolicy(self, secpol):
        from repoze.bfg.interfaces import ISecurityPolicy
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerUtility(secpol, ISecurityPolicy)

    def _registerEventListener(self, iface):
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        L = []
        def listener(event):
            L.append(event)
        gsm.registerHandler(listener, (iface,))
        return L

    def _registerRootFactory(self, root_factory):
        from repoze.bfg.interfaces import IRootFactory
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerUtility(root_factory, IRootFactory)

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

    def test_call_no_view_registered_no_isettings(self):
        rootfactory = make_rootfactory(None)
        environ = self._makeEnviron()
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        self._registerTraverserFactory(traversalfactory, '', None)
        logger = self._registerLogger()
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless('http://localhost:8080' in result[0], result)
        self.failIf('debug_notfound' in result[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_debug_notfound_false(self):
        rootfactory = make_rootfactory(None)
        environ = self._makeEnviron()
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        self._registerTraverserFactory(traversalfactory, '', None)
        logger = self._registerLogger()
        self._registerSettings(debug_notfound=False)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless('http://localhost:8080' in result[0], result)
        self.failIf('debug_notfound' in result[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_debug_notfound_true(self):
        rootfactory = make_rootfactory(None)
        environ = self._makeEnviron()
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerSettings(debug_notfound=True)
        logger = self._registerLogger()
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless(
            "debug_notfound of url http://localhost:8080; path_info: '', "
            "context:" in result[0])
        self.failUnless(
            "view_name: '', subpath: []" in result[0])
        self.failUnless('http://localhost:8080' in result[0], result)
        self.assertEqual(len(logger.messages), 1)
        message = logger.messages[0]
        self.failUnless('of url http://localhost:8080' in message)
        self.failUnless("path_info: ''" in message)
        self.failUnless('DummyContext instance at' in message)
        self.failUnless("view_name: ''" in message)
        self.failUnless("subpath: []" in message)

    def test_call_view_registered_nonspecific_default_path(self):
        rootfactory = make_rootfactory(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', None, None)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], '')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], [])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)
        self.assertEqual(environ['webob.adhoc_attrs']['root'], None)

    def test_call_view_registered_nonspecific_nondefault_path_and_subpath(self):
        rootfactory = make_rootfactory(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, 'foo', ['bar'])
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, 'foo', None, None)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], 'foo')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], ['bar'])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)
        self.assertEqual(environ['webob.adhoc_attrs']['root'], None)

    def test_call_view_registered_specific_success(self):
        rootfactory = make_rootfactory(None)
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
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', IContext, IRequest)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], '')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], [])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)
        self.assertEqual(environ['webob.adhoc_attrs']['root'], None)

    def test_call_view_registered_specific_fail(self):
        rootfactory = make_rootfactory(None)
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
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', IContext, IRequest)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '404 Not Found')
        self.failUnless('404' in result[0])

    def test_call_view_registered_security_policy_permission_none(self):
        rootfactory = make_rootfactory(None)
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
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', IContext, IRequest)
        secpol = DummySecurityPolicy()
        self._registerSecurityPolicy(secpol)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '200 OK')

    def test_call_view_registered_security_policy_permission_succeeds(self):
        rootfactory = make_rootfactory(None)
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
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, '', IContext, IRequest)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(permissionfactory.checked_with, secpol)

    def test_call_view_permission_fails_nosettings(self):
        rootfactory = make_rootfactory(None)
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
        from repoze.bfg.security import ACLDenied
        permissionfactory = make_permission_factory(
            ACLDenied('ace', 'acl', 'permission', ['principals'], context)
            )
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, '', IContext, IRequest)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '401 Unauthorized')
        message = result[0]
        self.failUnless('failed security policy check' in message)
        self.assertEqual(permissionfactory.checked_with, secpol)

    def test_call_view_permission_fails_no_debug_auth(self):
        rootfactory = make_rootfactory(None)
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
        from repoze.bfg.security import ACLDenied
        permissionfactory = make_permission_factory(
            ACLDenied('ace', 'acl', 'permission', ['principals'], context)
            )
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, '', IContext, IRequest)
        self._registerSettings(debug_authorization=False)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '401 Unauthorized')
        message = result[0]
        self.failUnless('failed security policy check' in message)
        self.assertEqual(permissionfactory.checked_with, secpol)

    def test_call_view_permission_fails_with_debug_auth(self):
        rootfactory = make_rootfactory(None)
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
        from repoze.bfg.security import ACLDenied
        permissionfactory = make_permission_factory(
            ACLDenied('ace', 'acl', 'permission', ['principals'], context)
            )
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, '', IContext, IRequest)
        self._registerSettings(debug_authorization=True)
        logger = self._registerLogger()
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '401 Unauthorized')
        message = result[0]
        self.failUnless(
            "ACLDenied permission 'permission' via ACE 'ace' in ACL 'acl' "
            "on context" in message)
        self.failUnless("for principals ['principals']" in message)
        self.assertEqual(permissionfactory.checked_with, secpol)
        self.assertEqual(len(logger.messages), 1)
        logged = logger.messages[0]
        self.failUnless(
            "debug_authorization of url http://localhost:8080 (view name "
            "'' against context" in logged)
        self.failUnless(
            "ACLDenied permission 'permission' via ACE 'ace' in ACL 'acl' on "
            "context" in logged)
        self.failUnless(
            "for principals ['principals']" in logged)

    def test_call_eventsends(self):
        rootfactory = make_rootfactory(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', None, None)
        from repoze.bfg.interfaces import INewRequest
        from repoze.bfg.interfaces import INewResponse
        request_events = self._registerEventListener(INewRequest)
        response_events = self._registerEventListener(INewResponse)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(len(request_events), 1)
        self.assertEqual(request_events[0].request.environ, environ)
        self.assertEqual(len(response_events), 1)
        self.assertEqual(response_events[0].response, response)

    def test_call_post_method(self):
        from repoze.bfg.interfaces import INewRequest
        from repoze.bfg.interfaces import IPOSTRequest
        from repoze.bfg.interfaces import IPUTRequest
        from repoze.bfg.interfaces import IRequest
        rootfactory = make_rootfactory(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron(REQUEST_METHOD='POST')
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', None, None)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        request_events = self._registerEventListener(INewRequest)
        result = router(environ, start_response)
        request = request_events[0].request
        self.failUnless(IPOSTRequest.providedBy(request))
        self.failIf(IPUTRequest.providedBy(request))
        self.failUnless(IRequest.providedBy(request))

    def test_call_put_method(self):
        from repoze.bfg.interfaces import INewRequest
        from repoze.bfg.interfaces import IPUTRequest
        from repoze.bfg.interfaces import IPOSTRequest
        from repoze.bfg.interfaces import IRequest
        rootfactory = make_rootfactory(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron(REQUEST_METHOD='PUT')
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', None, None)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        request_events = self._registerEventListener(INewRequest)
        result = router(environ, start_response)
        request = request_events[0].request
        self.failUnless(IPUTRequest.providedBy(request))
        self.failIf(IPOSTRequest.providedBy(request))
        self.failUnless(IRequest.providedBy(request))

    def test_call_irequestfactory_override(self):
        from repoze.bfg.interfaces import INewRequest
        from repoze.bfg.interfaces import IRequestFactory
        from webob import Request
        class Request2(Request):
            pass
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerUtility(Request2, IRequestFactory)
        rootfactory = make_rootfactory(None)
        context = DummyContext()
        traversalfactory = make_traversal_factory(context, '', [])
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerTraverserFactory(traversalfactory, '', None)
        self._registerView(view, '', None, None)
        self._registerRootFactory(rootfactory)
        router = self._makeOne(None)
        start_response = DummyStartResponse()
        request_events = self._registerEventListener(INewRequest)
        result = router(environ, start_response)
        request = request_events[0].request
        self.failUnless(isinstance(request, Request2))
    
class MakeAppTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.router import make_app
        return make_app(*arg, **kw)

    def test_fixtureapp(self):
        from repoze.bfg.tests import fixtureapp
        rootpolicy = make_rootfactory(None)
        app = self._callFUT(rootpolicy, fixtureapp)
        self.assertEqual(app.registry.__name__, 'repoze.bfg.tests.fixtureapp')

    def test_event(self):
        def subscriber(event):
            event.app.created = True        
        from repoze.bfg.interfaces import IWSGIApplicationCreatedEvent
        import repoze.bfg.router
        from zope.component import getGlobalSiteManager
        old_registry_manager = repoze.bfg.router.registry_manager
        repoze.bfg.router.registry_manager = DummyRegistryManager()
        getGlobalSiteManager().registerHandler(
            subscriber,
            (IWSGIApplicationCreatedEvent,)
            )
        try:
            from repoze.bfg.tests import fixtureapp
            rootpolicy = make_rootfactory(None)
            app = self._callFUT(rootpolicy, fixtureapp)
            assert app.created is True
        finally:
            repoze.bfg.router.registry_manager = old_registry_manager

    def test_registrations(self):
        options= {'reload_templates':True,
                  'debug_authorization':True}
        import repoze.bfg.router
        old_registry_manager = repoze.bfg.router.registry_manager
        dummy_registry_manager = DummyRegistryManager()
        repoze.bfg.router.registry_manager = dummy_registry_manager
        try:
            from repoze.bfg.tests import fixtureapp
            rootpolicy = make_rootfactory(None)
            app = self._callFUT(rootpolicy, fixtureapp, options=options)
            from repoze.bfg.interfaces import ISettings
            from repoze.bfg.interfaces import ILogger
            from repoze.bfg.interfaces import IRootFactory
            settings = app.registry.getUtility(ISettings)
            logger = app.registry.getUtility(ILogger, name='repoze.bfg.debug')
            rootfactory = app.registry.getUtility(IRootFactory)
            self.assertEqual(logger.name, 'repoze.bfg.debug')
            self.assertEqual(settings.reload_templates, True)
            self.assertEqual(settings.debug_authorization, True)
            self.assertEqual(rootfactory, rootpolicy)
            self.assertEqual(dummy_registry_manager.pushed, True)
            self.assertEqual(dummy_registry_manager.popped, True)
        finally:
            repoze.bfg.router.registry_manager = old_registry_manager

class DummyRegistryManager:
    def push(self, registry):
        self.pushed = True

    def pop(self):
        self.popped = True

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
        def __init__(self, root):
            self.root = root

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

def make_rootfactory(root):
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
    
class DummySecurityPolicy:
    pass

