import unittest

from repoze.bfg.testing import cleanUp

class BaseTest(object):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _registerView(self, reg, app, name):
        from repoze.bfg.interfaces import IRequest
        for_ = (IRequest, IContext)
        from repoze.bfg.interfaces import IView
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
        from repoze.bfg.interfaces import IRequest
        from zope.interface import directlyProvides
        from webob import Request
        from repoze.bfg.registry import Registry
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
        from repoze.bfg.view import render_view_to_response
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
        from repoze.bfg.view import render_view_to_iterable
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
        from repoze.bfg.view import render_view
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
        from repoze.bfg.view import is_response
        return is_response(*arg, **kw)

    def test_is(self):
        response = DummyResponse()
        self.assertEqual(self._callFUT(response), True)

    def test_isnt(self):
        response = None
        self.assertEqual(self._callFUT(response), False)

    def test_partial_inst(self):
        response = DummyResponse()
        response.app_iter = None
        self.assertEqual(self._callFUT(response), False)
        
    def test_status_not_string(self):
        response = DummyResponse()
        response.status = None
        self.assertEqual(self._callFUT(response), False)

class TestStaticView(BaseTest, unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.view import static
        return static

    def _makeOne(self, path, package_name=None):
        return self._getTargetClass()(path, package_name=package_name)
        
    def test_abspath(self):
        import os
        path = os.path.dirname(__file__)
        view = self._makeOne(path)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(response.directory, path)

    def test_relpath(self):
        path = 'fixtures'
        view = self._makeOne(path)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(response.root_resource, 'fixtures')
        self.assertEqual(response.resource_name, 'fixtures')
        self.assertEqual(response.package_name, 'repoze.bfg.tests')
        self.assertEqual(response.cache_max_age, 3600)

    def test_relpath_withpackage(self):
        view = self._makeOne('another:fixtures')
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(response.root_resource, 'fixtures')
        self.assertEqual(response.resource_name, 'fixtures')
        self.assertEqual(response.package_name, 'another')
        self.assertEqual(response.cache_max_age, 3600)

    def test_relpath_withpackage_name(self):
        view = self._makeOne('fixtures', package_name='another')
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(response.root_resource, 'fixtures')
        self.assertEqual(response.resource_name, 'fixtures')
        self.assertEqual(response.package_name, 'another')
        self.assertEqual(response.cache_max_age, 3600)

class TestBFGViewDecorator(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.view import bfg_view
        return bfg_view

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
                                  permission='foo')
        self.assertEqual(decorator.name, None)
        self.assertEqual(decorator.request_type, None)
        self.assertEqual(decorator.context, None)
        self.assertEqual(decorator.permission, 'foo')
        
    def test_call_function(self):
        decorator = self._makeOne()
        def foo():
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__[0]
        self.assertEqual(settings['permission'], None)
        self.assertEqual(settings['context'], None)
        self.assertEqual(settings['request_type'], None)

    def test_call_oldstyle_class(self):
        decorator = self._makeOne()
        class foo:
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__[0]
        self.assertEqual(settings['permission'], None)
        self.assertEqual(settings['context'], None)
        self.assertEqual(settings['request_type'], None)

    def test_call_newstyle_class(self):
        decorator = self._makeOne()
        class foo(object):
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__[0]
        self.assertEqual(settings['permission'], None)
        self.assertEqual(settings['context'], None)
        self.assertEqual(settings['request_type'], None)

    def test_stacking(self):
        decorator1 = self._makeOne(name='1')
        decorator2 = self._makeOne(name='2')
        def foo():
            """ docstring """
        wrapped1 = decorator1(foo)
        wrapped2 = decorator2(wrapped1)
        self.failUnless(wrapped1 is foo)
        self.failUnless(wrapped2 is foo)
        self.assertEqual(len(foo.__bfg_view_settings__), 2)
        settings1 = foo.__bfg_view_settings__[0]
        self.assertEqual(settings1['name'], '1')
        settings2 = foo.__bfg_view_settings__[1]
        self.assertEqual(settings2['name'], '2')

    def test_call_as_method(self):
        decorator = self._makeOne()
        def foo(self): pass
        def bar(self): pass
        class foo(object):
            """ docstring """
            foomethod = decorator(foo)
            barmethod = decorator(bar)
        settings = foo.__bfg_view_settings__
        self.assertEqual(len(settings), 2)
        self.assertEqual(settings[0]['attr'], 'foo')
        self.assertEqual(settings[1]['attr'], 'bar')

    def test_with_custom_predicates(self):
        decorator = self._makeOne(custom_predicates=(1,))
        def foo(context, request): return 'OK'
        decorated = decorator(foo)
        settings = decorated.__bfg_view_settings__
        self.assertEqual(settings[0]['custom_predicates'], (1,))

    def test_call_with_renderer_nodot(self):
        decorator = self._makeOne(renderer='json')
        def foo():
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__[0]
        self.assertEqual(settings['renderer'], 'json')

    def test_call_with_renderer_relpath(self):
        decorator = self._makeOne(renderer='fixtures/minimal.pt')
        def foo():
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__[0]
        self.assertEqual(settings['renderer'],
                         'repoze.bfg.tests:fixtures/minimal.pt')

    def test_call_with_renderer_pkgpath(self):
        decorator = self._makeOne(
            renderer='repoze.bfg.tests:fixtures/minimal.pt')
        def foo():
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__[0]
        self.assertEqual(settings['renderer'],
                         'repoze.bfg.tests:fixtures/minimal.pt')

class TestDefaultForbiddenView(BaseTest, unittest.TestCase):
    def _callFUT(self, context, request):
        from repoze.bfg.view import default_forbidden_view
        return default_forbidden_view(context, request)

    def test_nomessage(self):
        request = self._makeRequest()
        context = self._makeContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')
        self.failUnless('<code></code>' in response.body)

    def test_withmessage(self):
        request = self._makeRequest()
        request.environ['repoze.bfg.message'] = 'abc&123'
        context = self._makeContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')
        self.failUnless('<code>abc&amp;123</code>' in response.body)

class TestDefaultNotFoundView(BaseTest, unittest.TestCase):
    def _callFUT(self, context, request):
        from repoze.bfg.view import default_notfound_view
        return default_notfound_view(context, request)

    def test_nomessage(self):
        request = self._makeRequest()
        context = self._makeContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')
        self.failUnless('<code></code>' in response.body)

    def test_withmessage(self):
        request = self._makeRequest()
        request.environ['repoze.bfg.message'] = 'abc&123'
        context = self._makeContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')
        self.failUnless('<code>abc&amp;123</code>' in response.body)

class AppendSlashNotFoundView(BaseTest, unittest.TestCase):
    def _callFUT(self, context, request):
        from repoze.bfg.view import append_slash_notfound_view
        return append_slash_notfound_view(context, request)

    def _registerMapper(self, reg, match=True):
        from repoze.bfg.interfaces import IRoutesMapper
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

    def test_no_mapper(self):
        request = self._makeRequest(PATH_INFO='/abc')
        context = DummyContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_no_path(self):
        request = self._makeRequest()
        context = self._makeContext()
        self._registerMapper(request.registry, True)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_mapper_path_already_slash_ending(self):
        request = self._makeRequest(PATH_INFO='/abc/')
        context = DummyContext()
        self._registerMapper(request.registry, True)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_matches(self):
        request = self._makeRequest(PATH_INFO='/abc')
        context = DummyContext()
        self._registerMapper(request.registry, True)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, '/abc/')


class DummyContext:
    pass

class DummyRequest:
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        
    def get_response(self, application):
        return application

    def copy(self):
        self.copied = True
        return self

def make_view(response):
    def view(context, request):
        return response
    return view

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
