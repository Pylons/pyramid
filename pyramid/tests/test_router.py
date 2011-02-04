import unittest

from pyramid import testing

class TestRouter(unittest.TestCase):
    def setUp(self):
        testing.setUp()
        from pyramid.threadlocal import get_current_registry
        self.registry = get_current_registry()

    def tearDown(self):
        testing.tearDown()

    def _registerRouteRequest(self, name):
        from pyramid.interfaces import IRouteRequest
        from pyramid.request import route_request_iface
        iface = route_request_iface(name)
        self.registry.registerUtility(iface, IRouteRequest, name=name)
        return iface

    def _connectRoute(self, name, path, factory=None):
        from pyramid.interfaces import IRoutesMapper
        from pyramid.urldispatch import RoutesMapper
        mapper = self.registry.queryUtility(IRoutesMapper)
        if mapper is None:
            mapper = RoutesMapper()
            self.registry.registerUtility(mapper, IRoutesMapper)
        mapper.connect(name, path, factory)

    def _registerLogger(self):
        from pyramid.interfaces import IDebugLogger
        logger = DummyLogger()
        self.registry.registerUtility(logger, IDebugLogger)
        return logger

    def _registerSettings(self, **kw):
        settings = {'debug_authorization':False,
                    'debug_notfound':False,
                    'debug_routematch':False}
        settings.update(kw)
        self.registry.settings = settings

    def _registerTraverserFactory(self, context, view_name='', subpath=None,
                                  traversed=None, virtual_root=None,
                                  virtual_root_path=None, raise_error=None,
                                  **kw):
        from pyramid.interfaces import ITraverser

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

            def __call__(self, request):
                if raise_error:
                    raise raise_error
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
                                      ITraverser, name='')

    def _registerView(self, app, name, classifier, req_iface, ctx_iface):
        from pyramid.interfaces import IView
        self.registry.registerAdapter(
            app, (classifier, req_iface, ctx_iface), IView, name)

    def _registerEventListener(self, iface):
        L = []
        def listener(event):
            L.append(event)
        self.registry.registerHandler(listener, (iface,))
        return L

    def _registerRootFactory(self, val):
        rootfactory = DummyRootFactory(val)
        from pyramid.interfaces import IRootFactory
        self.registry.registerUtility(rootfactory, IRootFactory)
        return rootfactory

    def _getTargetClass(self):
        from pyramid.router import Router
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
        context = DummyContext()
        self._registerTraverserFactory(context)
        rootfactory = self._registerRootFactory('abc')
        router = self._makeOne()
        self.assertEqual(router.root_policy, rootfactory)

    def test_request_factory(self):
        from pyramid.interfaces import IRequestFactory
        class DummyRequestFactory(object):
            pass
        self.registry.registerUtility(DummyRequestFactory, IRequestFactory)
        router = self._makeOne()
        self.assertEqual(router.request_factory, DummyRequestFactory)

    def test_call_traverser_default(self):
        from pyramid.exceptions import NotFound
        environ = self._makeEnviron()
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(NotFound, router, environ, start_response)
        self.failUnless('/' in why[0], why)
        self.failIf('debug_notfound' in why[0])
        self.assertEqual(len(logger.messages), 0)

    def test_traverser_raises_notfound_class(self):
        from pyramid.exceptions import NotFound
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context, raise_error=NotFound)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(NotFound, router, environ, start_response)

    def test_traverser_raises_notfound_instance(self):
        from pyramid.exceptions import NotFound
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context, raise_error=NotFound('foo'))
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(NotFound, router, environ, start_response)
        self.failUnless('foo' in why[0], why)

    def test_traverser_raises_forbidden_class(self):
        from pyramid.exceptions import Forbidden
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context, raise_error=Forbidden)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(Forbidden, router, environ, start_response)

    def test_traverser_raises_forbidden_instance(self):
        from pyramid.exceptions import Forbidden
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context, raise_error=Forbidden('foo'))
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(Forbidden, router, environ, start_response)
        self.failUnless('foo' in why[0], why)

    def test_call_no_view_registered_no_isettings(self):
        from pyramid.exceptions import NotFound
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(NotFound, router, environ, start_response)
        self.failUnless('/' in why[0], why)
        self.failIf('debug_notfound' in why[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_debug_notfound_false(self):
        from pyramid.exceptions import NotFound
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        logger = self._registerLogger()
        self._registerSettings(debug_notfound=False)
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(NotFound, router, environ, start_response)
        self.failUnless('/' in why[0], why)
        self.failIf('debug_notfound' in why[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_debug_notfound_true(self):
        from pyramid.exceptions import NotFound
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        self._registerSettings(debug_notfound=True)
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(NotFound, router, environ, start_response)
        self.failUnless(
            "debug_notfound of url http://localhost:8080/; path_info: '/', "
            "context:" in why[0])
        self.failUnless("view_name: '', subpath: []" in why[0])
        self.failUnless('http://localhost:8080' in why[0], why)

        self.assertEqual(len(logger.messages), 1)
        message = logger.messages[0]
        self.failUnless('of url http://localhost:8080' in message)
        self.failUnless("path_info: '/'" in message)
        self.failUnless('DummyContext instance at' in message)
        self.failUnless("view_name: ''" in message)
        self.failUnless("subpath: []" in message)

    def test_call_view_returns_nonresponse(self):
        from pyramid.interfaces import IViewClassifier
        context = DummyContext()
        self._registerTraverserFactory(context)
        environ = self._makeEnviron()
        view = DummyView('abc')
        self._registerView(view, '', IViewClassifier, None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(ValueError, router, environ, start_response)

    def test_call_view_registered_nonspecific_default_path(self):
        from pyramid.interfaces import IViewClassifier
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, None, None)
        self._registerRootFactory(context)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        request = view.request
        self.assertEqual(request.view_name, '')
        self.assertEqual(request.subpath, [])
        self.assertEqual(request.context, context)
        self.assertEqual(request.root, context)

    def test_call_view_registered_nonspecific_nondefault_path_and_subpath(self):
        from pyramid.interfaces import IViewClassifier
        context = DummyContext()
        self._registerTraverserFactory(context, view_name='foo',
                                       subpath=['bar'],
                                       traversed=['context'])
        self._registerRootFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, 'foo', IViewClassifier, None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        request = view.request
        self.assertEqual(request.view_name, 'foo')
        self.assertEqual(request.subpath, ['bar'])
        self.assertEqual(request.context, context)
        self.assertEqual(request.root, context)

    def test_call_view_registered_specific_success(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context)
        self._registerRootFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        request = view.request
        self.assertEqual(request.view_name, '')
        self.assertEqual(request.subpath, [])
        self.assertEqual(request.context, context)
        self.assertEqual(request.root, context)

    def test_call_view_registered_specific_fail(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from pyramid.exceptions import NotFound
        from pyramid.interfaces import IViewClassifier
        class IContext(Interface):
            pass
        class INotContext(Interface):
            pass
        from pyramid.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, INotContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(NotFound, router, environ, start_response)

    def test_call_view_raises_forbidden(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from pyramid.exceptions import Forbidden
        class IContext(Interface):
            pass
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = DummyView(response, raise_exception=Forbidden("unauthorized"))
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(Forbidden, router, environ, start_response)
        self.assertEqual(why[0], 'unauthorized')

    def test_call_view_raises_notfound(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.exceptions import NotFound
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = DummyView(response, raise_exception=NotFound("notfound"))
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(NotFound, router, environ, start_response)
        self.assertEqual(why[0], 'notfound')

    def test_call_request_has_response_callbacks(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse('200 OK')
        def view(context, request):
            def callback(request, response):
                response.called_back = True
            request.response_callbacks = [callback]
            return response
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        router(environ, start_response)
        self.assertEqual(response.called_back, True)

    def test_call_request_has_finished_callbacks_when_view_succeeds(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse('200 OK')
        def view(context, request):
            def callback(request):
                request.environ['called_back'] = True
            request.finished_callbacks = [callback]
            return response
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        router(environ, start_response)
        self.assertEqual(environ['called_back'], True)

    def test_call_request_has_finished_callbacks_when_view_raises(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        def view(context, request):
            def callback(request):
                request.environ['called_back'] = True
            request.finished_callbacks = [callback]
            raise NotImplementedError
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        exc_raised(NotImplementedError, router, environ, start_response)
        self.assertEqual(environ['called_back'], True)

    def test_call_request_factory_raises(self):
        # making sure finally doesnt barf when a request cannot be created
        environ = self._makeEnviron()
        router = self._makeOne()
        def dummy_request_factory(environ):
            raise NotImplementedError
        router.request_factory = dummy_request_factory
        start_response = DummyStartResponse()
        exc_raised(NotImplementedError, router, environ, start_response)

    def test_call_eventsends(self):
        from pyramid.interfaces import INewRequest
        from pyramid.interfaces import INewResponse
        from pyramid.interfaces import IContextFound
        from pyramid.interfaces import IViewClassifier
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, None, None)
        request_events = self._registerEventListener(INewRequest)
        aftertraversal_events = self._registerEventListener(IContextFound)
        response_events = self._registerEventListener(INewResponse)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(len(request_events), 1)
        self.assertEqual(request_events[0].request.environ, environ)
        self.assertEqual(len(aftertraversal_events), 1)
        self.assertEqual(aftertraversal_events[0].request.environ, environ)
        self.assertEqual(len(response_events), 1)
        self.assertEqual(response_events[0].response, response)
        self.assertEqual(result, response.app_iter)

    def test_call_pushes_and_pops_threadlocal_manager(self):
        from pyramid.interfaces import IViewClassifier
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        router.threadlocal_manager = DummyThreadLocalManager()
        router(environ, start_response)
        self.assertEqual(len(router.threadlocal_manager.pushed), 1)
        self.assertEqual(len(router.threadlocal_manager.popped), 1)

    def test_call_route_matches_and_has_factory(self):
        from pyramid.interfaces import IViewClassifier
        logger = self._registerLogger()
        self._registerSettings(debug_routematch=True)
        self._registerRouteRequest('foo')
        root = object()
        def factory(request):
            return root
        self._connectRoute('foo', 'archives/:action/:article', factory)
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        self._registerView(view, '', IViewClassifier, None, None)
        self._registerRootFactory(context)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        request = view.request
        self.assertEqual(request.view_name, '')
        self.assertEqual(request.subpath, [])
        self.assertEqual(request.context, context)
        self.assertEqual(request.root, root)
        matchdict = {'action':'action1', 'article':'article1'}
        self.assertEqual(environ['bfg.routes.matchdict'], matchdict)
        self.assertEqual(environ['bfg.routes.route'].name, 'foo')
        self.assertEqual(request.matchdict, matchdict)
        self.assertEqual(request.matched_route.name, 'foo')

        self.assertEqual(len(logger.messages), 1)
        self.failUnless(
            logger.messages[0].startswith(
            "route matched for url http://localhost:8080"
            "/archives/action1/article1; "
            "route_name: 'foo', "
            "path_info: '/archives/action1/article1', "
            "pattern: 'archives/:action/:article', "))

    def test_call_route_match_miss_debug_routematch(self):
        from pyramid.exceptions import NotFound
        logger = self._registerLogger()
        self._registerSettings(debug_routematch=True)
        self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article')
        context = DummyContext()
        self._registerTraverserFactory(context)
        environ = self._makeEnviron(PATH_INFO='/wontmatch')
        self._registerRootFactory(context)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(NotFound, router, environ, start_response)

        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(
            logger.messages[0],
            'no route matched for url http://localhost:8080/wontmatch')

    def test_call_route_matches_doesnt_overwrite_subscriber_iface(self):
        from pyramid.interfaces import INewRequest
        from pyramid.interfaces import IViewClassifier
        from zope.interface import alsoProvides
        from zope.interface import Interface
        self._registerRouteRequest('foo')
        class IFoo(Interface):
            pass
        def listener(event):
            alsoProvides(event.request, IFoo)
        self.registry.registerHandler(listener, (INewRequest,))
        root = object()
        def factory(request):
            return root
        self._connectRoute('foo', 'archives/:action/:article', factory)
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        self._registerView(view, '', IViewClassifier, None, None)
        self._registerRootFactory(context)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        request = view.request
        self.assertEqual(request.view_name, '')
        self.assertEqual(request.subpath, [])
        self.assertEqual(request.context, context)
        self.assertEqual(request.root, root)
        matchdict = {'action':'action1', 'article':'article1'}
        self.assertEqual(environ['bfg.routes.matchdict'], matchdict)
        self.assertEqual(environ['bfg.routes.route'].name, 'foo')
        self.assertEqual(request.matchdict, matchdict)
        self.assertEqual(request.matched_route.name, 'foo')
        self.failUnless(IFoo.providedBy(request))

    def test_root_factory_raises_notfound(self):
        from pyramid.interfaces import IRootFactory
        from pyramid.exceptions import NotFound
        from zope.interface import Interface
        from zope.interface import directlyProvides
        def rootfactory(request):
            raise NotFound('from root factory')
        self.registry.registerUtility(rootfactory, IRootFactory)
        class IContext(Interface):
            pass
        context = DummyContext()
        directlyProvides(context, IContext)
        environ = self._makeEnviron()
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(NotFound, router, environ, start_response)
        self.failUnless('from root factory' in why[0])

    def test_root_factory_raises_forbidden(self):
        from pyramid.interfaces import IRootFactory
        from pyramid.exceptions import Forbidden
        from zope.interface import Interface
        from zope.interface import directlyProvides
        def rootfactory(request):
            raise Forbidden('from root factory')
        self.registry.registerUtility(rootfactory, IRootFactory)
        class IContext(Interface):
            pass
        context = DummyContext()
        directlyProvides(context, IContext)
        environ = self._makeEnviron()
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(Forbidden, router, environ, start_response)
        self.failUnless('from root factory' in why[0])

    def test_root_factory_exception_propagating(self):
        from pyramid.interfaces import IRootFactory
        from zope.interface import Interface
        from zope.interface import directlyProvides
        def rootfactory(request):
            raise RuntimeError()
        self.registry.registerUtility(rootfactory, IRootFactory)
        class IContext(Interface):
            pass
        context = DummyContext()
        directlyProvides(context, IContext)
        environ = self._makeEnviron()
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(RuntimeError, router, environ, start_response)

    def test_traverser_exception_propagating(self):
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context, raise_error=RuntimeError())
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(RuntimeError, router, environ, start_response)

    def test_call_view_exception_propagating(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRequestFactory
        def rfactory(environ):
            return request
        self.registry.registerUtility(rfactory, IRequestFactory)
        from pyramid.request import Request
        request = Request.blank('/')
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = DummyView(response, raise_exception=RuntimeError)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(RuntimeError, router, environ, start_response)
        # ``exception`` must be attached to request even if a suitable
        # exception view cannot be found
        self.assertEqual(request.exception.__class__, RuntimeError)

    def test_call_view_raises_exception_view(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IRequest
        response = DummyResponse()
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        view = DummyView(response, raise_exception=RuntimeError)
        exception_view = DummyView(exception_response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, None)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, RuntimeError)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])
        self.assertEqual(view.request.exception.__class__, RuntimeError)

    def test_call_view_raises_super_exception_sub_exception_view(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IRequest
        class SuperException(Exception):
            pass
        class SubException(SuperException):
            pass
        response = DummyResponse()
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        view = DummyView(response, raise_exception=SuperException)
        exception_view = DummyView(exception_response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, None)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, SubException)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(SuperException, router, environ, start_response)

    def test_call_view_raises_sub_exception_super_exception_view(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IRequest
        class SuperException(Exception):
            pass
        class SubException(SuperException):
            pass
        response = DummyResponse()
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        view = DummyView(response, raise_exception=SubException)
        exception_view = DummyView(exception_response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, None)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, SuperException)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_call_view_raises_exception_another_exception_view(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IRequest
        class MyException(Exception):
            pass
        class AnotherException(Exception):
            pass
        response = DummyResponse()
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        view = DummyView(response, raise_exception=MyException)
        exception_view = DummyView(exception_response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, None)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, AnotherException)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(MyException, router, environ, start_response)

    def test_root_factory_raises_exception_view(self):
        from pyramid.interfaces import IRootFactory
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IExceptionViewClassifier
        def rootfactory(request):
            raise RuntimeError()
        self.registry.registerUtility(rootfactory, IRootFactory)
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        exception_view = DummyView(exception_response)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, RuntimeError)
        environ = self._makeEnviron()
        router = self._makeOne()
        start_response = DummyStartResponse()
        app_iter = router(environ, start_response)
        self.assertEqual(app_iter, ["Hello, world"])

    def test_traverser_raises_exception_view(self):
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IExceptionViewClassifier
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context, raise_error=RuntimeError())
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        exception_view = DummyView(exception_response)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, RuntimeError)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_exception_view_returns_non_response(self):
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        environ = self._makeEnviron()
        response = DummyResponse()
        view = DummyView(response, raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, IRequest, None)
        exception_view = DummyView(None)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, RuntimeError)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(ValueError, router, environ, start_response)

    def test_call_route_raises_route_exception_view(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           req_iface, RuntimeError)
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_call_view_raises_exception_route_view(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IRequest
        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, IRequest, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           req_iface, RuntimeError)
        environ = self._makeEnviron()
        start_response = DummyStartResponse()
        router = self._makeOne()
        self.assertRaises(RuntimeError, router, environ, start_response)

    def test_call_route_raises_exception_view(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IRequest
        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, RuntimeError)
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_call_route_raises_super_exception_sub_exception_view(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IRequest
        class SuperException(Exception):
            pass
        class SubException(SuperException):
            pass
        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=SuperException)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, SubException)
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        self.assertRaises(SuperException, router, environ, start_response)

    def test_call_route_raises_sub_exception_super_exception_view(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IRequest
        class SuperException(Exception):
            pass
        class SubException(SuperException):
            pass
        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=SubException)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, SuperException)
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_call_route_raises_exception_another_exception_view(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IRequest
        class MyException(Exception):
            pass
        class AnotherException(Exception):
            pass
        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=MyException)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, AnotherException)
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        self.assertRaises(MyException, router, environ, start_response)

    def test_call_route_raises_exception_view_specializing(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IRequest
        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           IRequest, RuntimeError)
        response_spec = DummyResponse()
        response_spec.app_iter = ["Hello, special world"]
        exception_view_spec = DummyView(response_spec)
        self._registerView(exception_view_spec, '', IExceptionViewClassifier,
                           req_iface, RuntimeError)
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, special world"])

    def test_call_route_raises_exception_view_another_route(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        req_iface = self._registerRouteRequest('foo')
        another_req_iface = self._registerRouteRequest('bar')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           another_req_iface, RuntimeError)
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        self.assertRaises(RuntimeError, router, environ, start_response)

    def test_call_view_raises_exception_view_route(self):
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        req_iface = self._registerRouteRequest('foo')
        response = DummyResponse()
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        view = DummyView(response, raise_exception=RuntimeError)
        exception_view = DummyView(exception_response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, None)
        self._registerView(exception_view, '', IExceptionViewClassifier,
                           req_iface, RuntimeError)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(RuntimeError, router, environ, start_response)

class DummyContext:
    pass

class DummyView:
    def __init__(self, response, raise_exception=None):
        self.response = response
        self.raise_exception = raise_exception

    def __call__(self, context, request):
        self.context = context
        self.request = request
        if not self.raise_exception is None:
            raise self.raise_exception
        return self.response

class DummyRootFactory:
    def __init__(self, root):
        self.root = root

    def __call__(self, environ):
        return self.root

class DummyStartResponse:
    status = ()
    headers = ()
    def __call__(self, status, headers):
        self.status = status
        self.headers = headers
        
class DummyResponse:
    headerlist = ()
    app_iter = ()
    def __init__(self, status='200 OK'):
        self.status = status
    
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

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    warn = info
    debug = info

def exc_raised(exc, func, *arg, **kw):
    try:
        func(*arg, **kw)
    except exc, e:
        return e
    else:
        raise AssertionError('%s not raised' % exc) # pragma: no cover

    
