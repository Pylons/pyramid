import unittest
import sys

from pyramid.testing import cleanUp

class BaseTest(object):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _registerView(self, reg, app, name):
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IViewClassifier
        for_ = (IViewClassifier, IRequest, IContext)
        from pyramid.interfaces import IView
        reg.registerAdapter(app, for_, IView, name)

    def _makeEnviron(self, **extras):
        environ = {
            'wsgi.url_scheme':'http',
            'wsgi.version':(1,0),
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'8080',
            'REQUEST_METHOD':'GET',
            }
        environ.update(extras)
        return environ

    def _makeRequest(self, **environ):
        from pyramid.interfaces import IRequest
        from zope.interface import directlyProvides
        from webob import Request
        from pyramid.registry import Registry
        environ = self._makeEnviron(**environ)
        request = Request(environ)
        request.registry = Registry()
        directlyProvides(request, IRequest)
        return request

    def _makeContext(self):
        from zope.interface import directlyProvides
        context = DummyContext()
        directlyProvides(context, IContext)
        return context
        

class RenderViewToResponseTests(BaseTest, unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from pyramid.view import render_view_to_response
        return render_view_to_response(*arg, **kw)
    
    def test_call_no_view_registered(self):
        request = self._makeRequest()
        context = self._makeContext()
        result = self._callFUT(context, request, name='notregistered')
        self.assertEqual(result, None)

    def test_call_no_registry_on_request(self):
        request = self._makeRequest()
        del request.registry
        context = self._makeContext()
        result = self._callFUT(context, request, name='notregistered')
        self.assertEqual(result, None)

    def test_call_view_registered_secure(self):
        request = self._makeRequest()
        context = self._makeContext()
        response = DummyResponse()
        view = make_view(response)
        self._registerView(request.registry, view, 'registered')
        response = self._callFUT(context, request, name='registered',
                                 secure=True)
        self.assertEqual(response.status, '200 OK')

    def test_call_view_registered_insecure_no_call_permissive(self):
        context = self._makeContext()
        request = self._makeRequest()
        response = DummyResponse()
        view = make_view(response)
        self._registerView(request.registry, view, 'registered')
        response = self._callFUT(context, request, name='registered',
                                 secure=False)
        self.assertEqual(response.status, '200 OK')

    def test_call_view_registered_insecure_with_call_permissive(self):
        context = self._makeContext()
        request = self._makeRequest()
        response = DummyResponse()
        view = make_view(response)
        def anotherview(context, request):
            return DummyResponse('anotherview')
        view.__call_permissive__ = anotherview
        self._registerView(request.registry, view, 'registered')
        response = self._callFUT(context, request, name='registered',
                                 secure=False)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.app_iter, ['anotherview'])

class RenderViewToIterableTests(BaseTest, unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from pyramid.view import render_view_to_iterable
        return render_view_to_iterable(*arg, **kw)
    
    def test_call_no_view_registered(self):
        request = self._makeRequest()
        context = self._makeContext()
        result = self._callFUT(context, request, name='notregistered')
        self.assertEqual(result, None)

    def test_call_view_registered_secure(self):
        request = self._makeRequest()
        context = self._makeContext()
        response = DummyResponse()
        view = make_view(response)
        self._registerView(request.registry, view, 'registered')
        iterable = self._callFUT(context, request, name='registered',
                                 secure=True)
        self.assertEqual(iterable, ())

    def test_call_view_registered_insecure_no_call_permissive(self):
        context = self._makeContext()
        request = self._makeRequest()
        response = DummyResponse()
        view = make_view(response)
        self._registerView(request.registry, view, 'registered')
        iterable = self._callFUT(context, request, name='registered',
                                 secure=False)
        self.assertEqual(iterable, ())

    def test_call_view_registered_insecure_with_call_permissive(self):
        context = self._makeContext()
        request = self._makeRequest()
        response = DummyResponse()
        view = make_view(response)
        def anotherview(context, request):
            return DummyResponse('anotherview')
        view.__call_permissive__ = anotherview
        self._registerView(request.registry, view, 'registered')
        iterable = self._callFUT(context, request, name='registered',
                                 secure=False)
        self.assertEqual(iterable, ['anotherview'])

class RenderViewTests(BaseTest, unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from pyramid.view import render_view
        return render_view(*arg, **kw)
    
    def test_call_no_view_registered(self):
        request = self._makeRequest()
        context = self._makeContext()
        result = self._callFUT(context, request, name='notregistered')
        self.assertEqual(result, None)

    def test_call_view_registered_secure(self):
        request = self._makeRequest()
        context = self._makeContext()
        response = DummyResponse()
        view = make_view(response)
        self._registerView(request.registry, view, 'registered')
        s = self._callFUT(context, request, name='registered', secure=True)
        self.assertEqual(s, '')

    def test_call_view_registered_insecure_no_call_permissive(self):
        context = self._makeContext()
        request = self._makeRequest()
        response = DummyResponse()
        view = make_view(response)
        self._registerView(request.registry, view, 'registered')
        s = self._callFUT(context, request, name='registered', secure=False)
        self.assertEqual(s, '')

    def test_call_view_registered_insecure_with_call_permissive(self):
        context = self._makeContext()
        request = self._makeRequest()
        response = DummyResponse()
        view = make_view(response)
        def anotherview(context, request):
            return DummyResponse('anotherview')
        view.__call_permissive__ = anotherview
        self._registerView(request.registry, view, 'registered')
        s = self._callFUT(context, request, name='registered', secure=False)
        self.assertEqual(s, 'anotherview')

class TestIsResponse(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from pyramid.view import is_response
        return is_response(*arg, **kw)

    def test_is(self):
        response = DummyResponse()
        self.assertEqual(self._callFUT(response), True)

    def test_isnt(self):
        response = None
        self.assertEqual(self._callFUT(response), False)

    def test_isnt_no_headerlist(self):
        class Response(object):
            pass
        resp = Response
        resp.status = '200 OK'
        resp.app_iter = []
        self.assertEqual(self._callFUT(resp), False)

    def test_isnt_no_status(self):
        class Response(object):
            pass
        resp = Response
        resp.app_iter = []
        resp.headerlist = ()
        self.assertEqual(self._callFUT(resp), False)

    def test_isnt_no_app_iter(self):
        class Response(object):
            pass
        resp = Response
        resp.status = '200 OK'
        resp.headerlist = ()
        self.assertEqual(self._callFUT(resp), False)

class TestViewConfigDecorator(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from pyramid.view import view_config
        return view_config

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_create_defaults(self):
        decorator = self._makeOne()
        self.assertEqual(decorator.name, '')
        self.assertEqual(decorator.request_type, None)
        self.assertEqual(decorator.context, None)
        self.assertEqual(decorator.permission, None)
        
    def test_create_nondefaults(self):
        decorator = self._makeOne(name=None, request_type=None, for_=None,
                                  permission='foo', mapper='mapper',
                                  decorator='decorator')
        self.assertEqual(decorator.name, None)
        self.assertEqual(decorator.request_type, None)
        self.assertEqual(decorator.context, None)
        self.assertEqual(decorator.permission, 'foo')
        self.assertEqual(decorator.mapper, 'mapper')
        self.assertEqual(decorator.decorator, 'decorator')
        
    def test_call_function(self):
        decorator = self._makeOne()
        venusian = DummyVenusian()
        decorator.venusian = venusian
        def foo(): pass
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = call_venusian(venusian)
        self.assertEqual(len(settings), 1)
        self.assertEqual(settings[0]['permission'], None)
        self.assertEqual(settings[0]['context'], None)
        self.assertEqual(settings[0]['request_type'], None)

    def test_call_class(self):
        decorator = self._makeOne()
        venusian = DummyVenusian()
        decorator.venusian = venusian
        decorator.venusian.info.scope = 'class'
        class foo(object): pass
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = call_venusian(venusian)
        self.assertEqual(len(settings), 1)
        self.assertEqual(settings[0]['permission'], None)
        self.assertEqual(settings[0]['context'], None)
        self.assertEqual(settings[0]['request_type'], None)

    def test_stacking(self):
        decorator1 = self._makeOne(name='1')
        venusian1 = DummyVenusian()
        decorator1.venusian = venusian1
        venusian2 = DummyVenusian()
        decorator2 = self._makeOne(name='2')
        decorator2.venusian = venusian2
        def foo(): pass
        wrapped1 = decorator1(foo)
        wrapped2 = decorator2(wrapped1)
        self.failUnless(wrapped1 is foo)
        self.failUnless(wrapped2 is foo)
        settings1 = call_venusian(venusian1)
        self.assertEqual(len(settings1), 1)
        self.assertEqual(settings1[0]['name'], '1')
        settings2 = call_venusian(venusian2)
        self.assertEqual(len(settings2), 1)
        self.assertEqual(settings2[0]['name'], '2')

    def test_call_as_method(self):
        decorator = self._makeOne()
        venusian = DummyVenusian()
        decorator.venusian = venusian
        decorator.venusian.info.scope = 'class'
        def foo(self): pass
        def bar(self): pass
        class foo(object):
            foomethod = decorator(foo)
            barmethod = decorator(bar)
        settings = call_venusian(venusian)
        self.assertEqual(len(settings), 2)
        self.assertEqual(settings[0]['attr'], 'foo')
        self.assertEqual(settings[1]['attr'], 'bar')

    def test_with_custom_predicates(self):
        decorator = self._makeOne(custom_predicates=(1,))
        venusian = DummyVenusian()
        decorator.venusian = venusian
        def foo(context, request): pass
        decorated = decorator(foo)
        self.failUnless(decorated is foo)
        settings = call_venusian(venusian)
        self.assertEqual(settings[0]['custom_predicates'], (1,))

    def test_call_with_renderer_string(self):
        import pyramid.tests
        decorator = self._makeOne(renderer='fixtures/minimal.pt')
        venusian = DummyVenusian()
        decorator.venusian = venusian
        def foo(): pass
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = call_venusian(venusian)
        self.assertEqual(len(settings), 1)
        renderer = settings[0]['renderer']
        self.assertEqual(renderer.name, 'fixtures/minimal.pt')
        self.assertEqual(renderer.package, pyramid.tests)
        self.assertEqual(renderer.registry.__class__, DummyRegistry)

    def test_call_with_renderer_dict(self):
        decorator = self._makeOne(renderer={'a':1})
        venusian = DummyVenusian()
        decorator.venusian = venusian
        def foo(): pass
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = call_venusian(venusian)
        self.assertEqual(len(settings), 1)
        self.assertEqual(settings[0]['renderer'], {'a':1})

class Test_append_slash_notfound_view(BaseTest, unittest.TestCase):
    def _callFUT(self, context, request):
        from pyramid.view import append_slash_notfound_view
        return append_slash_notfound_view(context, request)

    def _registerMapper(self, reg, match=True):
        from pyramid.interfaces import IRoutesMapper
        class DummyRoute(object):
            def __init__(self, val):
                self.val = val
            def match(self, path):
                return self.val
        class DummyMapper(object):
            def __init__(self):
                self.routelist = [ DummyRoute(match) ]
            def get_routes(self):
                return self.routelist
        mapper = DummyMapper()
        reg.registerUtility(mapper, IRoutesMapper)
        return mapper

    def test_context_is_not_exception(self):
        request = self._makeRequest(PATH_INFO='/abc')
        request.exception = ExceptionResponse()
        context = DummyContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.app_iter, ['Not Found'])

    def test_no_mapper(self):
        request = self._makeRequest(PATH_INFO='/abc')
        context = ExceptionResponse()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_no_path(self):
        request = self._makeRequest()
        context = ExceptionResponse()
        self._registerMapper(request.registry, True)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_mapper_path_already_slash_ending(self):
        request = self._makeRequest(PATH_INFO='/abc/')
        context = ExceptionResponse()
        self._registerMapper(request.registry, True)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_matches(self):
        request = self._makeRequest(PATH_INFO='/abc')
        context = ExceptionResponse()
        self._registerMapper(request.registry, True)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, '/abc/')

    def test_with_query_string(self):
        request = self._makeRequest(PATH_INFO='/abc', QUERY_STRING='a=1&b=2')
        context = ExceptionResponse()
        self._registerMapper(request.registry, True)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, '/abc/?a=1&b=2')

class TestAppendSlashNotFoundViewFactory(BaseTest, unittest.TestCase):
    def _makeOne(self, notfound_view):
        from pyramid.view import AppendSlashNotFoundViewFactory
        return AppendSlashNotFoundViewFactory(notfound_view)
    
    def test_custom_notfound_view(self):
        request = self._makeRequest(PATH_INFO='/abc')
        context = ExceptionResponse()
        def custom_notfound(context, request):
            return 'OK'
        view = self._makeOne(custom_notfound)
        response = view(context, request)
        self.assertEqual(response, 'OK')

class Test_default_exceptionresponse_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from pyramid.view import default_exceptionresponse_view
        return default_exceptionresponse_view(context, request)

    def test_is_exception(self):
        context = Exception()
        result = self._callFUT(context, None)
        self.failUnless(result is context)

    def test_is_not_exception_no_request_exception(self):
        context = object()
        request = DummyRequest()
        result = self._callFUT(context, request)
        self.failUnless(result is context)

    def test_is_not_exception_request_exception(self):
        context = object()
        request = DummyRequest()
        request.exception = 'abc'
        result = self._callFUT(context, request)
        self.assertEqual(result, 'abc')

class ExceptionResponse(Exception):
    status = '404 Not Found'
    app_iter = ['Not Found']
    headerlist = []

class DummyContext:
    pass

def make_view(response):
    def view(context, request):
        return response
    return view

class DummyRequest:
    exception = None

class DummyResponse:
    status = '200 OK'
    headerlist = ()
    def __init__(self, body=None):
        if body is None:
            self.app_iter = ()
        else:
            self.app_iter = [body]

from zope.interface import Interface
class IContext(Interface):
    pass

class DummyVenusianInfo(object):
    scope = 'notaclass'
    module = sys.modules['pyramid.tests']
    codeinfo = 'codeinfo'

class DummyVenusian(object):
    def __init__(self, info=None):
        if info is None:
            info = DummyVenusianInfo()
        self.info = info
        self.attachments = []

    def attach(self, wrapped, callback, category=None):
        self.attachments.append((wrapped, callback, category))
        return self.info

class DummyRegistry(object):
    pass

class DummyConfig(object):
    def __init__(self):
        self.settings = []
        self.registry = DummyRegistry()

    def add_view(self, **kw):
        self.settings.append(kw)

class DummyVenusianContext(object):
    def __init__(self):
        self.config = DummyConfig()
        
def call_venusian(venusian):
    context = DummyVenusianContext()
    for wrapped, callback, category in venusian.attachments:
        callback(context, None, None)
    return context.config.settings

