import unittest
from zope.interface import implementer

from pyramid import testing
from pyramid.interfaces import IResponse


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.registry = self.config.registry

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
        return mapper.connect(name, path, factory)

    def _registerLogger(self):
        from pyramid.interfaces import IDebugLogger

        logger = DummyLogger()
        self.registry.registerUtility(logger, IDebugLogger)
        return logger

    def _registerSettings(self, **kw):
        settings = {
            'debug_authorization': False,
            'debug_notfound': False,
            'debug_routematch': False,
        }
        settings.update(kw)
        self.registry.settings = settings

    def _registerTraverserFactory(
        self,
        context,
        view_name='',
        subpath=None,
        traversed=None,
        virtual_root=None,
        virtual_root_path=None,
        raise_error=None,
        **kw,
    ):
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
                values = {
                    'root': self.root,
                    'context': context,
                    'view_name': view_name,
                    'subpath': subpath,
                    'traversed': traversed,
                    'virtual_root': virtual_root,
                    'virtual_root_path': virtual_root_path,
                }
                kw.update(values)
                return kw

        self.registry.registerAdapter(
            DummyTraverserFactory, (None,), ITraverser, name=''
        )

    def _registerView(self, app, name, classifier, req_iface, ctx_iface):
        from pyramid.interfaces import IView

        self.registry.registerAdapter(
            app, (classifier, req_iface, ctx_iface), IView, name
        )

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

    def _mockFinishRequest(self, router):
        """
        Mock :meth:`pyramid.router.Router.finish_request` to be a no-op.  This
        prevents :prop:`pyramid.request.Request.context` from being removed, so
        we can write assertions against it.

        """

        def mock_finish_request(request):
            pass

        router.finish_request = mock_finish_request

    def _makeEnviron(self, **extras):
        environ = {
            'wsgi.url_scheme': 'http',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '8080',
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
        }
        environ.update(extras)
        return environ

    def test_ctor_registry_has_no_settings(self):
        self.registry.settings = None
        router = self._makeOne()
        self.assertEqual(router.debug_notfound, False)
        self.assertEqual(router.debug_routematch, False)
        self.assertFalse('debug_notfound' in router.__dict__)
        self.assertFalse('debug_routematch' in router.__dict__)

    def test_root_policy(self):
        context = DummyContext()
        self._registerTraverserFactory(context)
        rootfactory = self._registerRootFactory('abc')
        router = self._makeOne()
        self.assertEqual(router.root_policy, rootfactory)

    def test_request_factory(self):
        from pyramid.interfaces import IRequestFactory

        class DummyRequestFactory:
            pass

        self.registry.registerUtility(DummyRequestFactory, IRequestFactory)
        router = self._makeOne()
        self.assertEqual(router.request_factory, DummyRequestFactory)

    def test_tween_factories(self):
        from pyramid.config.tweens import Tweens
        from pyramid.interfaces import IResponse, ITweens, IViewClassifier
        from pyramid.response import Response

        tweens = Tweens()
        self.registry.registerUtility(tweens, ITweens)
        L = []

        def tween_factory1(handler, registry):
            L.append((handler, registry))

            def wrapper(request):
                request.environ['handled'].append('one')
                return handler(request)

            wrapper.name = 'one'
            wrapper.child = handler
            return wrapper

        def tween_factory2(handler, registry):
            L.append((handler, registry))

            def wrapper(request):
                request.environ['handled'] = ['two']
                return handler(request)

            wrapper.name = 'two'
            wrapper.child = handler
            return wrapper

        tweens.add_implicit('one', tween_factory1)
        tweens.add_implicit('two', tween_factory2)
        router = self._makeOne()
        self.assertEqual(router.handle_request.name, 'two')
        self.assertEqual(router.handle_request.child.name, 'one')
        self.assertEqual(
            router.handle_request.child.child.__name__, 'handle_request'
        )
        context = DummyContext()
        self._registerTraverserFactory(context)
        environ = self._makeEnviron()
        view = DummyView('abc')
        self._registerView(
            self.config.derive_view(view), '', IViewClassifier, None, None
        )
        start_response = DummyStartResponse()

        def make_response(s):
            return Response(s)

        router.registry.registerAdapter(make_response, (str,), IResponse)
        app_iter = router(environ, start_response)
        self.assertEqual(app_iter, [b'abc'])
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['handled'], ['two', 'one'])

    def test_call_traverser_default(self):
        from pyramid.httpexceptions import HTTPNotFound

        environ = self._makeEnviron()
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(HTTPNotFound, router, environ, start_response)
        self.assertTrue('/' in why.args[0], why)
        self.assertFalse('debug_notfound' in why.args[0])
        self.assertEqual(len(logger.messages), 0)

    def test_traverser_raises_notfound_class(self):
        from pyramid.httpexceptions import HTTPNotFound

        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context, raise_error=HTTPNotFound)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(HTTPNotFound, router, environ, start_response)

    def test_traverser_raises_notfound_instance(self):
        from pyramid.httpexceptions import HTTPNotFound

        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(
            context, raise_error=HTTPNotFound('foo')
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(HTTPNotFound, router, environ, start_response)
        self.assertTrue('foo' in why.args[0], why)

    def test_traverser_raises_forbidden_class(self):
        from pyramid.httpexceptions import HTTPForbidden

        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context, raise_error=HTTPForbidden)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(HTTPForbidden, router, environ, start_response)

    def test_traverser_raises_forbidden_instance(self):
        from pyramid.httpexceptions import HTTPForbidden

        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(
            context, raise_error=HTTPForbidden('foo')
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(HTTPForbidden, router, environ, start_response)
        self.assertTrue('foo' in why.args[0], why)

    def test_call_no_view_registered_no_isettings(self):
        from pyramid.httpexceptions import HTTPNotFound

        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(HTTPNotFound, router, environ, start_response)
        self.assertTrue('/' in why.args[0], why)
        self.assertFalse('debug_notfound' in why.args[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_debug_notfound_false(self):
        from pyramid.httpexceptions import HTTPNotFound

        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        logger = self._registerLogger()
        self._registerSettings(debug_notfound=False)
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(HTTPNotFound, router, environ, start_response)
        self.assertTrue('/' in why.args[0], why)
        self.assertFalse('debug_notfound' in why.args[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_debug_notfound_true(self):
        from pyramid.httpexceptions import HTTPNotFound

        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        self._registerSettings(debug_notfound=True)
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(HTTPNotFound, router, environ, start_response)
        self.assertTrue(
            "debug_notfound of url http://localhost:8080/; " in why.args[0]
        )
        self.assertTrue("view_name: '', subpath: []" in why.args[0])
        self.assertTrue('http://localhost:8080' in why.args[0], why)

        self.assertEqual(len(logger.messages), 1)
        message = logger.messages[0]
        self.assertTrue('of url http://localhost:8080' in message)
        self.assertTrue("path_info: " in message)
        self.assertTrue('DummyContext' in message)
        self.assertTrue("view_name: ''" in message)
        self.assertTrue("subpath: []" in message)

    def test_call_view_returns_non_iresponse(self):
        from pyramid.interfaces import IViewClassifier

        context = DummyContext()
        self._registerTraverserFactory(context)
        environ = self._makeEnviron()
        view = DummyView('abc')
        self._registerView(
            self.config.derive_view(view), '', IViewClassifier, None, None
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(ValueError, router, environ, start_response)

    def test_call_view_returns_adapted_response(self):
        from pyramid.interfaces import IResponse, IViewClassifier
        from pyramid.response import Response

        context = DummyContext()
        self._registerTraverserFactory(context)
        environ = self._makeEnviron()
        view = DummyView('abc')
        self._registerView(
            self.config.derive_view(view), '', IViewClassifier, None, None
        )
        router = self._makeOne()
        start_response = DummyStartResponse()

        def make_response(s):
            return Response(s)

        router.registry.registerAdapter(make_response, (str,), IResponse)
        app_iter = router(environ, start_response)
        self.assertEqual(app_iter, [b'abc'])
        self.assertEqual(start_response.status, '200 OK')

    def test_call_with_request_extensions(self):
        from pyramid.interfaces import (
            IRequest,
            IRequestExtensions,
            IViewClassifier,
        )
        from pyramid.request import Request
        from pyramid.util import InstancePropertyHelper

        context = DummyContext()
        self._registerTraverserFactory(context)

        class Extensions:
            def __init__(self):
                self.methods = {}
                self.descriptors = {}

        extensions = Extensions()
        ext_method = lambda r: 'bar'
        name, fn = InstancePropertyHelper.make_property(ext_method, name='foo')
        extensions.descriptors[name] = fn
        request = Request.blank('/')
        request.request_iface = IRequest
        request.registry = self.registry

        def request_factory(environ):
            return request

        self.registry.registerUtility(extensions, IRequestExtensions)
        environ = self._makeEnviron()
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        self._registerView(
            self.config.derive_view(view), '', IViewClassifier, None, None
        )
        router = self._makeOne()
        router.request_factory = request_factory
        start_response = DummyStartResponse()
        router(environ, start_response)
        self.assertEqual(view.request.foo, 'bar')

    def test_call_view_registered_nonspecific_default_path(self):
        from pyramid.interfaces import IViewClassifier

        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(
            self.config.derive_view(view), '', IViewClassifier, None, None
        )
        self._registerRootFactory(context)
        router = self._makeOne()
        self._mockFinishRequest(router)
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

    def test_call_view_registered_nonspecific_nondefault_path_and_subpath(
        self,
    ):
        from pyramid.interfaces import IViewClassifier

        context = DummyContext()
        self._registerTraverserFactory(
            context, view_name='foo', subpath=['bar'], traversed=['context']
        )
        self._registerRootFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, 'foo', IViewClassifier, None, None)
        router = self._makeOne()
        self._mockFinishRequest(router)
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
        from zope.interface import Interface, directlyProvides

        class IContext(Interface):
            pass

        from pyramid.interfaces import IRequest, IViewClassifier

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
        self._mockFinishRequest(router)
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
        from zope.interface import Interface, directlyProvides

        from pyramid.httpexceptions import HTTPNotFound
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
        self.assertRaises(HTTPNotFound, router, environ, start_response)

    def test_call_view_raises_forbidden(self):
        from zope.interface import Interface, directlyProvides

        from pyramid.httpexceptions import HTTPForbidden

        class IContext(Interface):
            pass

        from pyramid.interfaces import IRequest, IViewClassifier

        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = DummyView(
            response, raise_exception=HTTPForbidden("unauthorized")
        )
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(HTTPForbidden, router, environ, start_response)
        self.assertEqual(why.args[0], 'unauthorized')

    def test_call_view_raises_notfound(self):
        from zope.interface import Interface, directlyProvides

        class IContext(Interface):
            pass

        from pyramid.httpexceptions import HTTPNotFound
        from pyramid.interfaces import IRequest, IViewClassifier

        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = DummyView(response, raise_exception=HTTPNotFound("notfound"))
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(HTTPNotFound, router, environ, start_response)
        self.assertEqual(why.args[0], 'notfound')

    def test_call_view_raises_response_cleared(self):
        from zope.interface import Interface, directlyProvides

        from pyramid.interfaces import IExceptionViewClassifier

        class IContext(Interface):
            pass

        from pyramid.interfaces import IRequest, IViewClassifier

        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])

        def view(context, request):
            request.response.a = 1
            raise KeyError

        def exc_view(context, request):
            self.assertFalse(hasattr(request.response, 'a'))
            request.response.body = b'OK'
            return request.response

        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        self._registerView(
            exc_view, '', IExceptionViewClassifier, IRequest, KeyError
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        itera = router(environ, start_response)
        self.assertEqual(itera, [b'OK'])

    def test_call_request_has_response_callbacks(self):
        from zope.interface import Interface, directlyProvides

        class IContext(Interface):
            pass

        from pyramid.interfaces import IRequest, IViewClassifier

        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse('200 OK')

        def view(context, request):
            def callback(request, response):
                response.called_back = True

            request.add_response_callback(callback)
            return response

        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        router(environ, start_response)
        self.assertEqual(response.called_back, True)

    def test_finish_request_when_view_succeeds(self):
        from zope.interface import Interface, directlyProvides

        class IContext(Interface):
            pass

        from pyramid.interfaces import IRequest, IViewClassifier

        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse('200 OK')

        def view(context, request):
            def callback(request):
                request.environ['called_back'] = True

            request.add_finished_callback(callback)
            request.environ['request'] = request
            return response

        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        router(environ, start_response)
        self.assertEqual(environ['called_back'], True)
        self.assertFalse(hasattr(environ['request'], 'context'))

    def test_finish_request_when_view_raises(self):
        from zope.interface import Interface, directlyProvides

        class IContext(Interface):
            pass

        from pyramid.interfaces import IRequest, IViewClassifier

        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])

        def view(context, request):
            def callback(request):
                request.environ['called_back'] = True

            request.add_finished_callback(callback)
            request.environ['request'] = request
            raise NotImplementedError

        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        router = self._makeOne()
        start_response = DummyStartResponse()
        exc_raised(NotImplementedError, router, environ, start_response)
        self.assertEqual(environ['called_back'], True)
        self.assertFalse(hasattr(environ['request'], 'context'))

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
        from pyramid.interfaces import (
            IBeforeTraversal,
            IContextFound,
            INewRequest,
            INewResponse,
            IViewClassifier,
        )

        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, None, None)
        request_events = self._registerEventListener(INewRequest)
        beforetraversal_events = self._registerEventListener(IBeforeTraversal)
        context_found_events = self._registerEventListener(IContextFound)
        response_events = self._registerEventListener(INewResponse)
        router = self._makeOne()
        self._mockFinishRequest(router)
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(len(request_events), 1)
        self.assertEqual(request_events[0].request.environ, environ)
        self.assertEqual(len(beforetraversal_events), 1)
        self.assertEqual(beforetraversal_events[0].request.environ, environ)
        self.assertEqual(len(context_found_events), 1)
        self.assertEqual(context_found_events[0].request.environ, environ)
        self.assertEqual(context_found_events[0].request.context, context)
        self.assertEqual(len(response_events), 1)
        self.assertEqual(response_events[0].response, response)
        self.assertEqual(response_events[0].request.context, context)
        self.assertEqual(result, response.app_iter)

    def test_call_newrequest_evllist_exc_can_be_caught_by_exceptionview(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            INewRequest,
            IRequest,
        )

        context = DummyContext()
        self._registerTraverserFactory(context)
        environ = self._makeEnviron()

        def listener(event):
            raise KeyError

        self.registry.registerHandler(listener, (INewRequest,))
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        exception_view = DummyView(exception_response)
        environ = self._makeEnviron()
        self._registerView(
            exception_view, '', IExceptionViewClassifier, IRequest, KeyError
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, exception_response.app_iter)

    def test_call_route_matches_and_has_factory(self):
        from pyramid.interfaces import IViewClassifier

        logger = self._registerLogger()
        self._registerSettings(debug_routematch=True)
        self._registerRouteRequest('foo')
        root = object()

        def factory(request):
            return root

        route = self._connectRoute('foo', 'archives/:action/:article', factory)
        route.predicates = [DummyPredicate()]
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        self._registerView(view, '', IViewClassifier, None, None)
        self._registerRootFactory(context)
        router = self._makeOne()
        self._mockFinishRequest(router)
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
        matchdict = {'action': 'action1', 'article': 'article1'}
        self.assertEqual(request.matchdict, matchdict)
        self.assertEqual(request.matched_route.name, 'foo')
        self.assertEqual(len(logger.messages), 1)
        self.assertTrue(
            logger.messages[0].startswith(
                "route matched for url http://localhost:8080"
                "/archives/action1/article1; "
                "route_name: 'foo', "
                "path_info: "
            )
        )
        self.assertTrue("predicates: 'predicate'" in logger.messages[0])

    def test_call_route_match_miss_debug_routematch(self):
        from pyramid.httpexceptions import HTTPNotFound

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
        self.assertRaises(HTTPNotFound, router, environ, start_response)

        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(
            logger.messages[0],
            'no route matched for url http://localhost:8080/wontmatch',
        )

    def test_call_route_matches_doesnt_overwrite_subscriber_iface(self):
        from zope.interface import Interface, alsoProvides

        from pyramid.interfaces import INewRequest, IViewClassifier

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
        self._mockFinishRequest(router)
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
        matchdict = {'action': 'action1', 'article': 'article1'}
        self.assertEqual(request.matchdict, matchdict)
        self.assertEqual(request.matched_route.name, 'foo')
        self.assertTrue(IFoo.providedBy(request))

    def test_root_factory_raises_notfound(self):
        from zope.interface import Interface, directlyProvides

        from pyramid.httpexceptions import HTTPNotFound
        from pyramid.interfaces import IRootFactory

        def rootfactory(request):
            raise HTTPNotFound('from root factory')

        self.registry.registerUtility(rootfactory, IRootFactory)

        class IContext(Interface):
            pass

        context = DummyContext()
        directlyProvides(context, IContext)
        environ = self._makeEnviron()
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(HTTPNotFound, router, environ, start_response)
        self.assertTrue('from root factory' in why.args[0])

    def test_root_factory_raises_forbidden(self):
        from zope.interface import Interface, directlyProvides

        from pyramid.httpexceptions import HTTPForbidden
        from pyramid.interfaces import IRootFactory

        def rootfactory(request):
            raise HTTPForbidden('from root factory')

        self.registry.registerUtility(rootfactory, IRootFactory)

        class IContext(Interface):
            pass

        context = DummyContext()
        directlyProvides(context, IContext)
        environ = self._makeEnviron()
        router = self._makeOne()
        start_response = DummyStartResponse()
        why = exc_raised(HTTPForbidden, router, environ, start_response)
        self.assertTrue('from root factory' in why.args[0])

    def test_root_factory_exception_propagating(self):
        from zope.interface import Interface, directlyProvides

        from pyramid.interfaces import IRootFactory

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
        from zope.interface import Interface, directlyProvides

        class IContext(Interface):
            pass

        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IRequestFactory,
            IViewClassifier,
        )

        def rfactory(environ):
            return request

        self.registry.registerUtility(rfactory, IRequestFactory)
        from pyramid.request import Request

        request = Request.blank('/')
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        response.app_iter = ['OK']
        error = RuntimeError()
        view = DummyView(response, raise_exception=error)
        environ = self._makeEnviron()

        def exception_view(context, request):
            self.assertEqual(request.exc_info[0], RuntimeError)
            return response

        self._registerView(view, '', IViewClassifier, IRequest, IContext)
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            RuntimeError,
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['OK'])
        # exc_info and exception should still be around on the request after
        # the excview tween has run (see
        # https://github.com/Pylons/pyramid/issues/1223)
        self.assertEqual(request.exception, error)
        self.assertEqual(request.exc_info[:2], (RuntimeError, error))

    def test_call_view_raises_exception_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

        response = DummyResponse()
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        view = DummyView(response, raise_exception=RuntimeError)

        def exception_view(context, request):
            self.assertEqual(request.exception.__class__, RuntimeError)
            return exception_response

        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, None)
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            RuntimeError,
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_call_view_raises_super_exception_sub_exception_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

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
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            SubException,
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(SuperException, router, environ, start_response)

    def test_call_view_raises_sub_exception_super_exception_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

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
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            SuperException,
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_call_view_raises_exception_another_exception_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

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
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            AnotherException,
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(MyException, router, environ, start_response)

    def test_root_factory_raises_exception_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IRootFactory,
        )

        def rootfactory(request):
            raise RuntimeError()

        self.registry.registerUtility(rootfactory, IRootFactory)
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        exception_view = DummyView(exception_response)
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            RuntimeError,
        )
        environ = self._makeEnviron()
        router = self._makeOne()
        start_response = DummyStartResponse()
        app_iter = router(environ, start_response)
        self.assertEqual(app_iter, ["Hello, world"])

    def test_traverser_raises_exception_view(self):
        from pyramid.interfaces import IExceptionViewClassifier, IRequest

        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context, raise_error=RuntimeError())
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        exception_view = DummyView(exception_response)
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            RuntimeError,
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_exception_view_returns_non_iresponse(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

        environ = self._makeEnviron()
        response = DummyResponse()
        view = DummyView(response, raise_exception=RuntimeError)

        self._registerView(
            self.config.derive_view(view), '', IViewClassifier, IRequest, None
        )
        exception_view = DummyView(None)
        self._registerView(
            self.config.derive_view(exception_view),
            '',
            IExceptionViewClassifier,
            IRequest,
            RuntimeError,
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(ValueError, router, environ, start_response)

    def test_call_route_raises_route_exception_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IViewClassifier,
        )

        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            req_iface,
            RuntimeError,
        )
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_call_view_raises_exception_route_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, IRequest, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            req_iface,
            RuntimeError,
        )
        environ = self._makeEnviron()
        start_response = DummyStartResponse()
        router = self._makeOne()
        self.assertRaises(RuntimeError, router, environ, start_response)

    def test_call_route_raises_exception_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            RuntimeError,
        )
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_call_route_raises_super_exception_sub_exception_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

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
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            SubException,
        )
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        self.assertRaises(SuperException, router, environ, start_response)

    def test_call_route_raises_sub_exception_super_exception_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

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
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            SuperException,
        )
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, world"])

    def test_call_route_raises_exception_another_exception_view(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

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
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            AnotherException,
        )
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        self.assertRaises(MyException, router, environ, start_response)

    def test_call_route_raises_exception_view_specializing(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            IRequest,
            RuntimeError,
        )
        response_spec = DummyResponse()
        response_spec.app_iter = ["Hello, special world"]
        exception_view_spec = DummyView(response_spec)
        self._registerView(
            exception_view_spec,
            '',
            IExceptionViewClassifier,
            req_iface,
            RuntimeError,
        )
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        result = router(environ, start_response)
        self.assertEqual(result, ["Hello, special world"])

    def test_call_route_raises_exception_view_another_route(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IViewClassifier,
        )

        req_iface = self._registerRouteRequest('foo')
        another_req_iface = self._registerRouteRequest('bar')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=RuntimeError)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view = DummyView(response)
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            another_req_iface,
            RuntimeError,
        )
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        self.assertRaises(RuntimeError, router, environ, start_response)

    def test_call_view_raises_exception_view_route(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

        req_iface = self._registerRouteRequest('foo')
        response = DummyResponse()
        exception_response = DummyResponse()
        exception_response.app_iter = ["Hello, world"]
        view = DummyView(response, raise_exception=RuntimeError)
        exception_view = DummyView(exception_response)
        environ = self._makeEnviron()
        self._registerView(view, '', IViewClassifier, IRequest, None)
        self._registerView(
            exception_view,
            '',
            IExceptionViewClassifier,
            req_iface,
            RuntimeError,
        )
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(RuntimeError, router, environ, start_response)

    def test_call_view_raises_predicate_mismatch(self):
        from pyramid.exceptions import PredicateMismatch
        from pyramid.interfaces import IRequest, IViewClassifier

        view = DummyView(DummyResponse(), raise_exception=PredicateMismatch)
        self._registerView(view, '', IViewClassifier, IRequest, None)
        environ = self._makeEnviron()
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(PredicateMismatch, router, environ, start_response)

    def test_call_view_predicate_mismatch_doesnt_hide_views(self):
        from pyramid.exceptions import PredicateMismatch
        from pyramid.interfaces import IRequest, IResponse, IViewClassifier
        from pyramid.response import Response

        class BaseContext:
            pass

        class DummyContext(BaseContext):
            pass

        context = DummyContext()
        self._registerTraverserFactory(context)
        view = DummyView(DummyResponse(), raise_exception=PredicateMismatch)
        self._registerView(view, '', IViewClassifier, IRequest, DummyContext)
        good_view = DummyView('abc')
        self._registerView(
            self.config.derive_view(good_view),
            '',
            IViewClassifier,
            IRequest,
            BaseContext,
        )
        router = self._makeOne()

        def make_response(s):
            return Response(s)

        router.registry.registerAdapter(make_response, (str,), IResponse)
        environ = self._makeEnviron()
        start_response = DummyStartResponse()
        app_iter = router(environ, start_response)
        self.assertEqual(app_iter, [b'abc'])

    def test_call_view_multiple_predicate_mismatches_dont_hide_views(self):
        from zope.interface import Interface, implementer

        from pyramid.exceptions import PredicateMismatch
        from pyramid.interfaces import IRequest, IResponse, IViewClassifier
        from pyramid.response import Response

        class IBaseContext(Interface):
            pass

        class IContext(IBaseContext):
            pass

        @implementer(IContext)
        class DummyContext:
            pass

        context = DummyContext()
        self._registerTraverserFactory(context)
        view1 = DummyView(DummyResponse(), raise_exception=PredicateMismatch)
        self._registerView(view1, '', IViewClassifier, IRequest, DummyContext)
        view2 = DummyView(DummyResponse(), raise_exception=PredicateMismatch)
        self._registerView(view2, '', IViewClassifier, IRequest, IContext)
        good_view = DummyView('abc')
        self._registerView(
            self.config.derive_view(good_view),
            '',
            IViewClassifier,
            IRequest,
            IBaseContext,
        )
        router = self._makeOne()

        def make_response(s):
            return Response(s)

        router.registry.registerAdapter(make_response, (str,), IResponse)
        environ = self._makeEnviron()
        start_response = DummyStartResponse()
        app_iter = router(environ, start_response)
        self.assertEqual(app_iter, [b'abc'])

    def test_call_view_predicate_mismatch_doesnt_find_unrelated_views(self):
        from zope.interface import Interface, implementer

        from pyramid.exceptions import PredicateMismatch
        from pyramid.interfaces import IRequest, IViewClassifier

        class IContext(Interface):
            pass

        class IOtherContext(Interface):
            pass

        @implementer(IContext)
        class DummyContext:
            pass

        context = DummyContext()
        self._registerTraverserFactory(context)
        view = DummyView(DummyResponse(), raise_exception=PredicateMismatch)
        self._registerView(view, '', IViewClassifier, IRequest, DummyContext)
        please_dont_call_me_view = DummyView('abc')
        self._registerView(
            self.config.derive_view(please_dont_call_me_view),
            '',
            IViewClassifier,
            IRequest,
            IOtherContext,
        )
        router = self._makeOne()
        environ = self._makeEnviron()
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(PredicateMismatch, router, environ, start_response)

    def test_custom_execution_policy(self):
        from pyramid.interfaces import IExecutionPolicy
        from pyramid.request import Request
        from pyramid.response import Response

        registry = self.config.registry

        def dummy_policy(environ, router):
            return Response(status=200, body=b'foo')

        registry.registerUtility(dummy_policy, IExecutionPolicy)
        router = self._makeOne()
        resp = Request.blank('/').get_response(router)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, b'foo')

    def test_execution_policy_bubbles_exception(self):
        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IRequest,
            IViewClassifier,
        )

        class Exception1(Exception):
            pass

        class Exception2(Exception):
            pass

        req_iface = self._registerRouteRequest('foo')
        self._connectRoute('foo', 'archives/:action/:article', None)
        view = DummyView(DummyResponse(), raise_exception=Exception1)
        self._registerView(view, '', IViewClassifier, req_iface, None)
        exception_view1 = DummyView(
            DummyResponse(), raise_exception=Exception2
        )
        self._registerView(
            exception_view1, '', IExceptionViewClassifier, IRequest, Exception1
        )
        response = DummyResponse()
        response.app_iter = ["Hello, world"]
        exception_view2 = DummyView(response)
        self._registerView(
            exception_view2, '', IExceptionViewClassifier, IRequest, Exception2
        )
        environ = self._makeEnviron(PATH_INFO='/archives/action1/article1')
        start_response = DummyStartResponse()
        router = self._makeOne()
        self.assertRaises(Exception2, lambda: router(environ, start_response))

    def test_request_context_with_statement(self):
        from pyramid.interfaces import IExecutionPolicy
        from pyramid.request import Request
        from pyramid.response import Response
        from pyramid.threadlocal import get_current_request

        registry = self.config.registry
        result = []

        def dummy_policy(environ, router):
            with router.request_context(environ):
                result.append(get_current_request())
            result.append(get_current_request())
            return Response(status=200, body=b'foo')

        registry.registerUtility(dummy_policy, IExecutionPolicy)
        router = self._makeOne()
        resp = Request.blank('/test_path').get_response(router)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, b'foo')
        self.assertEqual(result[0].path_info, '/test_path')
        self.assertEqual(result[1], None)

    def test_request_context_manually(self):
        from pyramid.interfaces import IExecutionPolicy
        from pyramid.request import Request
        from pyramid.response import Response
        from pyramid.threadlocal import get_current_request

        registry = self.config.registry
        result = []

        def dummy_policy(environ, router):
            ctx = router.request_context(environ)
            ctx.begin()
            result.append(get_current_request())
            ctx.end()
            result.append(get_current_request())
            return Response(status=200, body=b'foo')

        registry.registerUtility(dummy_policy, IExecutionPolicy)
        router = self._makeOne()
        resp = Request.blank('/test_path').get_response(router)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, b'foo')
        self.assertEqual(result[0].path_info, '/test_path')
        self.assertEqual(result[1], None)


class DummyPredicate:
    def __call__(self, info, request):
        return True

    def text(self):
        return 'predicate'


class DummyContext:
    pass


class DummyView:
    def __init__(self, response, raise_exception=None):
        self.response = response
        self.raise_exception = raise_exception

    def __call__(self, context, request):
        self.context = context
        self.request = request
        if self.raise_exception is not None:
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


@implementer(IResponse)
class DummyResponse:
    headerlist = ()
    app_iter = ()
    environ = None

    def __init__(self, status='200 OK'):
        self.status = status

    def __call__(self, environ, start_response):
        self.environ = environ
        start_response(self.status, self.headerlist)
        return self.app_iter


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
    except exc as e:
        return e
    else:
        raise AssertionError('%s not raised' % exc)  # pragma: no cover
