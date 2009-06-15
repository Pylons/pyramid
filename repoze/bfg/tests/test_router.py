import unittest

from repoze.bfg.testing import cleanUp

class RouterTests(unittest.TestCase):
    def setUp(self):
        from repoze.bfg.registry import Registry
        from zope.component import getSiteManager
        self.registry = Registry()
        getSiteManager.sethook(lambda *arg: self.registry)

    def tearDown(self):
        from zope.component import getSiteManager
        getSiteManager.reset()
        cleanUp()

    def _registerLogger(self):
        from repoze.bfg.interfaces import ILogger
        logger = DummyLogger()
        self.registry.registerUtility(logger, ILogger, name='repoze.bfg.debug')
        return logger

    def _registerSettings(self, **kw):
        from repoze.bfg.interfaces import ISettings
        class Settings:
            def __init__(self, **kw):
                self.__dict__.update(kw)

        defaultkw = {'debug_authorization':False, 'debug_notfound':False}
        defaultkw.update(kw)
        settings = Settings(**defaultkw)
        self.registry.registerUtility(settings, ISettings)

    def _registerAuthenticationPolicy(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        policy = DummyAuthenticationPolicy()
        self.registry.registerUtility(policy, IAuthenticationPolicy)
        return policy

    def _registerTraverserFactory(self, context, view_name='', subpath=None,
                                  traversed=None, virtual_root=None,
                                  virtual_root_path=None, **kw):
        from repoze.bfg.interfaces import ITraverserFactory

        if virtual_root is None:
            virtual_root = context
        if subpath is None:
            subpath = []
        if traversed is None:
            traversed = []
        if virtual_root_path is None:
            virtual_root_path = []

        class DummyTraverserFactory:
            def __init__(self, root):
                self.root = root

            def __call__(self, path):
                values = {'root':self.root,
                          'context':context,
                          'view_name':view_name,
                          'subpath':subpath,
                          'traversed':traversed,
                          'virtual_root':virtual_root,
                          'virtual_root_path':virtual_root_path}
                kw.update(values)
                return kw
            
        self.registry.registerAdapter(DummyTraverserFactory, (None,),
                                      ITraverserFactory, name='')

    def _registerView(self, app, name, *for_):
        from repoze.bfg.interfaces import IView
        self.registry.registerAdapter(app, for_, IView, name)

    def _registerViewPermission(self, view_name, allow=True):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IViewPermission
        class Checker(object):
            def __call__(self, context, request):
                self.context = context
                self.request = request
                return allow
        checker = Checker()
        self.registry.registerAdapter(checker, (Interface, Interface),
                                      IViewPermission,
                                      view_name)
        return checker

    def _registerEventListener(self, iface):
        L = []
        def listener(event):
            L.append(event)
        self.registry.registerHandler(listener, (iface,))
        return L

    def _registerRootFactory(self, val):
        rootfactory = make_rootfactory(val)
        from repoze.bfg.interfaces import IRootFactory
        self.registry.registerUtility(rootfactory, IRootFactory)
        return rootfactory

    def _getTargetClass(self):
        from repoze.bfg.router import Router
        return Router

    def _makeOne(self):
        klass = self._getTargetClass()
        return klass(self.registry)

    def _makeEnviron(self, **extras):
        environ = {
            'wsgi.url_scheme':'http',
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'8080',
            'REQUEST_METHOD':'GET',
            'PATH_INFO':'/',
            }
        environ.update(extras)
        return environ

    def test_root_policy(self):
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        rootfactory = self._registerRootFactory('abc')
        router = self._makeOne()
        self.assertEqual(router.root_policy, rootfactory)

    def test_iforbiddenview_override(self):
        from repoze.bfg.interfaces import IForbiddenView
        def app():
            """ """
        self.registry.registerUtility(app, IForbiddenView)
        router = self._makeOne()
        self.assertEqual(router.forbidden_view, app)

    def test_iforbiddenview_nooverride(self):
        context = DummyContext()
        router = self._makeOne()
        from repoze.bfg.router import default_forbidden_view
        self.assertEqual(router.forbidden_view, default_forbidden_view)

    def test_inotfoundview_override(self):
        from repoze.bfg.interfaces import INotFoundView
        def app():
            """ """
        self.registry.registerUtility(app, INotFoundView)
        router = self._makeOne()
        self.assertEqual(router.notfound_view, app)

    def test_inotfoundview_nooverride(self):
        context = DummyContext()
        router = self._makeOne()
        from repoze.bfg.router import default_notfound_view
        self.assertEqual(router.notfound_view, default_notfound_view)

    def test_iunauthorized_appfactory_BBB(self):
        from repoze.bfg.interfaces import IUnauthorizedAppFactory
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        logger = self._registerLogger()
        def factory():
            return 'yo'
        self.registry.registerUtility(factory, IUnauthorizedAppFactory)
        router = self._makeOne()
        self.assertEqual(len(logger.messages), 1)
        self.failUnless('IForbiddenView' in logger.messages[0])
        class DummyRequest:
            def get_response(self, app):
                return app
        req = DummyRequest()
        self.assertEqual(router.forbidden_view(None, req), 'yo')

    def test_inotfound_appfactory_BBB(self):
        from repoze.bfg.interfaces import INotFoundAppFactory
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        logger = self._registerLogger()
        def factory():
            return 'yo'
        self.registry.registerUtility(factory, INotFoundAppFactory)
        router = self._makeOne()
        self.assertEqual(len(logger.messages), 1)
        self.failUnless('INotFoundView' in logger.messages[0])
        class DummyRequest:
            def get_response(self, app):
                return app
        req = DummyRequest()
        self.assertEqual(router.notfound_view(None, req), 'yo')

    def test_call_no_view_registered_no_isettings(self):
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless('<code>/</code>' in result[0], result)
        self.failIf('debug_notfound' in result[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_debug_notfound_false(self):
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        logger = self._registerLogger()
        self._registerSettings(debug_notfound=False)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless('<code>/</code>' in result[0], result)
        self.failIf('debug_notfound' in result[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_debug_notfound_true(self):
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        self._registerSettings(debug_notfound=True)
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless(
            "debug_notfound of url http://localhost:8080/; path_info: '/', "
            "context:" in result[0])
        self.failUnless(
            "view_name: '', subpath: []" in result[0])
        self.failUnless('http://localhost:8080' in result[0], result)
        self.assertEqual(len(logger.messages), 1)
        message = logger.messages[0]
        self.failUnless('of url http://localhost:8080' in message)
        self.failUnless("path_info: '/'" in message)
        self.failUnless('DummyContext instance at' in message)
        self.failUnless("view_name: ''" in message)
        self.failUnless("subpath: []" in message)

    def test_call_view_returns_nonresponse(self):
        context = DummyContext()
        self._registerTraverserFactory(context)
        environ = self._makeEnviron()
        view = make_view('abc')
        self._registerView(view, '', None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(ValueError, router, environ, start_response)

    def test_inotfoundview_returns_nonresponse(self):
        from repoze.bfg.interfaces import INotFoundView
        context = DummyContext()
        environ = self._makeEnviron()
        self._registerTraverserFactory(context)
        def app(context, request):
            """ """
        self.registry.registerUtility(app, INotFoundView)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(ValueError, router, environ, start_response)

    def test_iforbiddenview_returns_nonresponse(self):
        from repoze.bfg.interfaces import IForbiddenView
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context)
        self._registerAuthenticationPolicy()
        response = DummyResponse()
        view = make_view(response)
        from repoze.bfg.security import ACLDenied
        denied = ACLDenied('ace', 'acl', 'permission', ['principals'], context)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        checker = self._registerViewPermission('', denied)
        def app(context, request):
            """ """
        self.registry.registerUtility(app, IForbiddenView)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(ValueError, router, environ, start_response)

    def test_call_view_registered_nonspecific_default_path(self):
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', None, None)
        rootfactory = self._registerRootFactory(context)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], '')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], [])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)
        self.assertEqual(environ['webob.adhoc_attrs']['root'], context)

    def test_call_deprecation_warning(self):
        context = DummyContext()
        self._registerTraverserFactory(context, _deprecation_warning='abc')
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', None, None)
        router = self._makeOne()
        logger = self._registerLogger()
        router.logger = logger
        start_response = DummyStartResponse()
        router(environ, start_response)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0], 'abc')

    def test_call_view_registered_nonspecific_nondefault_path_and_subpath(self):
        context = DummyContext()
        self._registerTraverserFactory(context, view_name='foo',
                                       subpath=['bar'],
                                       traversed=['context'])
        rootfactory = self._registerRootFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, 'foo', None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], 'foo')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], ['bar'])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)
        self.assertEqual(environ['webob.adhoc_attrs']['root'], context)

    def test_call_view_registered_specific_success(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context)
        rootfactory = self._registerRootFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], '')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], [])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)
        self.assertEqual(environ['webob.adhoc_attrs']['root'], context)

    def test_call_view_registered_specific_fail(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        class INotContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, INotContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '404 Not Found')
        self.failUnless('404' in result[0])

    def test_call_view_permission_none(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '200 OK')

    def test_call_view_no_authentication_policy_debug_authorization(self):
        logger = self._registerLogger()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne()
        router.debug_authorization = True
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(len(logger.messages), 1)
        self.failUnless('no authentication policy' in logger.messages[0])

    def test_call_view_no_permission_registered_debug_authorization(self):
        self._registerAuthenticationPolicy()
        logger = self._registerLogger()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne()
        router.debug_authorization = True
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(len(logger.messages), 1)
        self.failUnless('no permission registered' in logger.messages[0])

    def test_call_view_no_permission_registered_no_debug(self):
        self._registerAuthenticationPolicy()
        logger = self._registerLogger()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne()
        router.debug_authorization = False
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(len(logger.messages), 0)

    def test_call_view_permission_succeeds(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        self._registerAuthenticationPolicy()
        response = DummyResponse()
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        checker = self._registerViewPermission('', True)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(checker.context, context)

    def test_call_view_permission_fails_nosettings(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        self._registerAuthenticationPolicy()
        response = DummyResponse()
        view = make_view(response)
        from repoze.bfg.security import ACLDenied
        denied = ACLDenied('ace', 'acl', 'permission', ['principals'], context)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        checker = self._registerViewPermission('', denied)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '401 Unauthorized')
        message = environ['repoze.bfg.message']
        self.assertEqual(message, 'Unauthorized: failed security policy check')
        self.assertEqual(checker.context, context)

    def test_call_view_permission_fails_no_debug_auth(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        self._registerAuthenticationPolicy()
        response = DummyResponse()
        view = make_view(response)
        from repoze.bfg.security import ACLDenied
        denied = ACLDenied('ace', 'acl', 'permission', ['principals'], context)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        checker = self._registerViewPermission('', denied)
        self._registerSettings(debug_authorization=False)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '401 Unauthorized')
        message = environ['repoze.bfg.message']
        self.failUnless('failed security policy check' in message)
        self.assertEqual(checker.context, context)

    def test_call_view_permission_fails_with_debug_auth(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerAuthenticationPolicy()
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = make_view(response)
        from repoze.bfg.security import ACLDenied
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        allowed = ACLDenied('ace', 'acl', 'permission', ['principals'], context)
        checker = self._registerViewPermission('', allowed)
        self._registerSettings(debug_authorization=True)
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '401 Unauthorized')
        message = environ['repoze.bfg.message']
        self.failUnless(
            "ACLDenied permission 'permission' via ACE 'ace' in ACL 'acl' "
            "on context" in message)
        self.failUnless("for principals ['principals']" in message)
        self.assertEqual(checker.context, context)
        self.assertEqual(len(logger.messages), 1)
        logged = logger.messages[0]
        self.failUnless(
            "debug_authorization of url http://localhost:8080/ (view name "
            "'' against context" in logged)
        self.failUnless(
            "ACLDenied permission 'permission' via ACE 'ace' in ACL 'acl' on "
            "context" in logged)
        self.failUnless(
            "for principals ['principals']" in logged)

    def test_call_eventsends(self):
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', None, None)
        from repoze.bfg.interfaces import INewRequest
        from repoze.bfg.interfaces import INewResponse
        request_events = self._registerEventListener(INewRequest)
        response_events = self._registerEventListener(INewResponse)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(len(request_events), 1)
        self.assertEqual(request_events[0].request.environ, environ)
        self.assertEqual(len(response_events), 1)
        self.assertEqual(response_events[0].response, response)

    def test_call_pushes_and_pops_threadlocal_manager(self):
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron()
        self._registerView(view, '', None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        router.threadlocal_manager = DummyThreadLocalManager()
        result = router(environ, start_response)
        self.assertEqual(len(router.threadlocal_manager.pushed), 1)
        self.assertEqual(len(router.threadlocal_manager.popped), 1)

    def test_call_post_method(self):
        from repoze.bfg.interfaces import INewRequest
        from repoze.bfg.interfaces import IPOSTRequest
        from repoze.bfg.interfaces import IPUTRequest
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron(REQUEST_METHOD='POST')
        self._registerView(view, '', None, None)
        router = self._makeOne()
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
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron(REQUEST_METHOD='PUT')
        self._registerView(view, '', None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        request_events = self._registerEventListener(INewRequest)
        result = router(environ, start_response)
        request = request_events[0].request
        self.failUnless(IPUTRequest.providedBy(request))
        self.failIf(IPOSTRequest.providedBy(request))
        self.failUnless(IRequest.providedBy(request))

    def test_call_unknown_method(self):
        from repoze.bfg.interfaces import INewRequest
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = make_view(response)
        environ = self._makeEnviron(REQUEST_METHOD='UNKNOWN')
        self._registerView(view, '', None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        request_events = self._registerEventListener(INewRequest)
        result = router(environ, start_response)
        request = request_events[0].request
        self.failUnless(IRequest.providedBy(request))

class MakeAppTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        import repoze.bfg.router
        self.old_tl_manager = repoze.bfg.router.manager
        self.regmgr = DummyRegistryManager()
        repoze.bfg.router.manager = self.regmgr

    def tearDown(self):
        cleanUp()
        import repoze.bfg.router
        repoze.bfg.router.threadlocal_manager = self.old_tl_manager
        
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
        from zope.component import getGlobalSiteManager
        getGlobalSiteManager().registerHandler(
            subscriber,
            (IWSGIApplicationCreatedEvent,)
            )
        from repoze.bfg.tests import fixtureapp
        rootpolicy = make_rootfactory(None)
        app = self._callFUT(rootpolicy, fixtureapp)
        assert app.created is True

    def test_custom_settings(self):
        options= {'mysetting':True}
        from repoze.bfg.tests import fixtureapp
        rootpolicy = make_rootfactory(None)
        app = self._callFUT(rootpolicy, fixtureapp, options=options)
        from repoze.bfg.interfaces import ISettings
        settings = app.registry.getUtility(ISettings)
        self.assertEqual(settings.reload_templates, False)
        self.assertEqual(settings.debug_authorization, False)
        self.assertEqual(settings.mysetting, True)

    def test_registrations(self):
        options= {'reload_templates':True,
                  'debug_authorization':True}
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
        self.failUnless(self.regmgr.pushed and self.regmgr.popped)

    def test_routes_in_config_with_rootpolicy(self):
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.urldispatch import RoutesRootFactory
        from repoze.bfg.tests import routesapp
        rootpolicy = make_rootfactory(None)
        app = self._callFUT(rootpolicy, routesapp, options=options)
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        settings = app.registry.getUtility(ISettings)
        logger = app.registry.getUtility(ILogger, name='repoze.bfg.debug')
        rootfactory = app.registry.getUtility(IRootFactory)
        self.assertEqual(logger.name, 'repoze.bfg.debug')
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_authorization, True)
        self.failUnless(isinstance(rootfactory, RoutesRootFactory))
        self.assertEqual(rootfactory.default_root_factory, rootpolicy)
        self.failUnless(self.regmgr.pushed and self.regmgr.popped)

    def test_routes_in_config_no_rootpolicy(self):
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.urldispatch import RoutesRootFactory
        from repoze.bfg.router import DefaultRootFactory
        from repoze.bfg.tests import routesapp
        app = self._callFUT(None, routesapp, options=options)
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        settings = app.registry.getUtility(ISettings)
        logger = app.registry.getUtility(ILogger, name='repoze.bfg.debug')
        rootfactory = app.registry.getUtility(IRootFactory)
        self.assertEqual(logger.name, 'repoze.bfg.debug')
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_authorization, True)
        self.failUnless(isinstance(rootfactory, RoutesRootFactory))
        self.assertEqual(rootfactory.default_root_factory, DefaultRootFactory)
        self.failUnless(self.regmgr.pushed and self.regmgr.popped)
        
    def test_no_routes_in_config_no_rootpolicy(self):
        from repoze.bfg.router import DefaultRootFactory
        from repoze.bfg.interfaces import IRootFactory
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.tests import fixtureapp
        app = self._callFUT(None, fixtureapp, options=options)
        rootfactory = app.registry.getUtility(IRootFactory)
        self.assertEqual(rootfactory, DefaultRootFactory)

    def test_authorization_policy_no_authentication_policy(self):
        from repoze.bfg.interfaces import IAuthorizationPolicy
        authzpolicy = DummyContext()
        from repoze.bfg.tests import routesapp
        app = self._callFUT(None, routesapp, authorization_policy=authzpolicy)
        self.failIf(app.registry.queryUtility(IAuthorizationPolicy))
        
    def test_authentication_policy_no_authorization_policy(self):
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.authorization import ACLAuthorizationPolicy
        authnpolicy = DummyContext()
        from repoze.bfg.tests import routesapp
        app = self._callFUT(None, routesapp, authentication_policy=authnpolicy)
        self.assertEqual(app.registry.getUtility(IAuthenticationPolicy),
                         authnpolicy)
        self.assertEqual(
            app.registry.getUtility(IAuthorizationPolicy).__class__,
            ACLAuthorizationPolicy)
                        
    def test_authentication_policy_and_authorization_policy(self):
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthenticationPolicy
        authnpolicy = DummyContext()
        authzpolicy = DummyContext()
        from repoze.bfg.tests import routesapp
        app = self._callFUT(None, routesapp, authentication_policy=authnpolicy,
                            authorization_policy = authzpolicy)
        self.assertEqual(app.registry.getUtility(IAuthenticationPolicy),
                         authnpolicy)
        self.assertEqual(app.registry.getUtility(IAuthorizationPolicy),
                         authzpolicy)

    def test_secpol_BBB_registrations(self):
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import ISecurityPolicy
        secpol = DummySecurityPolicy()
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerUtility(secpol, ISecurityPolicy)
        from repoze.bfg.tests import routesapp
        logger = DummyLogger()
        app = self._callFUT(None, routesapp, registry=gsm, debug_logger=logger)
        self.failUnless(app.registry.queryUtility(IAuthenticationPolicy))
        self.failUnless(app.registry.queryUtility(IAuthorizationPolicy))
        self.assertEqual(len(logger.messages), 1)
        self.failUnless('ISecurityPolicy' in logger.messages[0])

class TestDefaultForbiddenView(unittest.TestCase):
    def _callFUT(self, context, request):
        from repoze.bfg.router import default_forbidden_view
        return default_forbidden_view(context, request)

    def test_nomessage(self):
        request = DummyRequest({})
        context = DummyContext()
        response = self._callFUT(context, request)
        self.failUnless('<code></code>' in response.body)

    def test_withmessage(self):
        request = DummyRequest({'repoze.bfg.message':'abc&123'})
        context = DummyContext()
        response = self._callFUT(context, request)
        self.failUnless('<code>abc&amp;123</code>' in response.body)

class TestDefaultRootFactory(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.router import DefaultRootFactory
        return DefaultRootFactory

    def _makeOne(self, environ):
        return self._getTargetClass()(environ)

    def test_no_matchdict(self):
        environ = {}
        root = self._makeOne(environ)
        self.assertEqual(root.__parent__, None)
        self.assertEqual(root.__name__, None)

    def test_matchdict(self):
        environ = {'bfg.routes.matchdict':{'a':1, 'b':2}}
        root = self._makeOne(environ)
        self.assertEqual(root.a, 1)
        self.assertEqual(root.b, 2)


class DummyRegistryManager:
    def push(self, registry):
        self.pushed = True

    def pop(self):
        self.popped = True

class DummyContext:
    pass

def make_view(response):
    def view(context, request):
        return response
    return view

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

class DummyRequest:
    def __init__(self, environ):
        self.environ = environ
        

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    warn = info
    debug = info

class DummyThreadLocalManager:
    def __init__(self):
        self.pushed = []
        self.popped = []

    def push(self, val):
        self.pushed.append(val)

    def pop(self):
        self.popped.append(True)
    
class DummyAuthenticationPolicy:
    pass
