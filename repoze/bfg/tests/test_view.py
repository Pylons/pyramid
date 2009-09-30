import unittest

from repoze.bfg.testing import cleanUp

class BaseTest(object):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _registerView(self, app, name, *for_):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import IView
        gsm.registerAdapter(app, for_, IView, name)

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

class RenderViewToResponseTests(BaseTest, unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.view import render_view_to_response
        return render_view_to_response(*arg, **kw)
    
    def test_call_no_view_registered(self):
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        context = DummyContext()
        result = self._callFUT(context, request, name='notregistered')
        self.assertEqual(result, None)

    def test_call_view_registered_secure(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        response = self._callFUT(context, request, name='registered',
                                 secure=True)
        self.assertEqual(response.status, '200 OK')


    def test_call_view_registered_insecure_no_call_permissive(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        response = self._callFUT(context, request, name='registered',
                                 secure=False)
        self.assertEqual(response.status, '200 OK')

    def test_call_view_registered_insecure_with_call_permissive(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        view = make_view(response)
        def anotherview(context, request):
            return DummyResponse('anotherview')
        view.__call_permissive__ = anotherview
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        response = self._callFUT(context, request, name='registered',
                                 secure=False)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.app_iter, ['anotherview'])

class RenderViewToIterableTests(BaseTest, unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.view import render_view_to_iterable
        return render_view_to_iterable(*arg, **kw)
    
    def test_call_no_view_registered(self):
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        context = DummyContext()
        result = self._callFUT(context, request, name='notregistered')
        self.assertEqual(result, None)

    def test_call_view_registered_secure(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        iterable = self._callFUT(context, request, name='registered',
                                 secure=True)
        self.assertEqual(iterable, ())

    def test_call_view_registered_insecure_no_call_permissive(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        iterable = self._callFUT(context, request, name='registered',
                                 secure=False)
        self.assertEqual(iterable, ())

    def test_call_view_registered_insecure_with_call_permissive(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        view = make_view(response)
        def anotherview(context, request):
            return DummyResponse('anotherview')
        view.__call_permissive__ = anotherview
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        iterable = self._callFUT(context, request, name='registered',
                                 secure=False)
        self.assertEqual(iterable, ['anotherview'])

class RenderViewTests(unittest.TestCase, BaseTest):
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.view import render_view
        return render_view(*arg, **kw)
    
    def test_call_no_view_registered(self):
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        context = DummyContext()
        result = self._callFUT(context, request, name='notregistered')
        self.assertEqual(result, None)

    def test_call_view_registered_secure(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        s = self._callFUT(context, request, name='registered', secure=True)
        self.assertEqual(s, '')

    def test_call_view_registered_insecure_no_call_permissive(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        s = self._callFUT(context, request, name='registered', secure=False)
        self.assertEqual(s, '')

    def test_call_view_registered_insecure_with_call_permissive(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        view = make_view(response)
        def anotherview(context, request):
            return DummyResponse('anotherview')
        view.__call_permissive__ = anotherview
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
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

class TestStaticView(unittest.TestCase, BaseTest):
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
        import os
        path = 'fixtures'
        view = self._makeOne(path)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        here = os.path.abspath(os.path.dirname(__file__))
        self.assertEqual(response.root_resource, 'fixtures')
        self.assertEqual(response.resource_name, 'fixtures')
        self.assertEqual(response.package_name, 'repoze.bfg.tests')
        self.assertEqual(response.cache_max_age, 3600)

    def test_relpath_withpackage(self):
        import os
        path = 'fixtures'
        view = self._makeOne('another:fixtures')
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        here = os.path.abspath(os.path.dirname(__file__))
        self.assertEqual(response.root_resource, 'fixtures')
        self.assertEqual(response.resource_name, 'fixtures')
        self.assertEqual(response.package_name, 'another')
        self.assertEqual(response.cache_max_age, 3600)

    def test_relpath_withpackage_name(self):
        import os
        path = 'fixtures'
        view = self._makeOne('fixtures', package_name='another')
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        here = os.path.abspath(os.path.dirname(__file__))
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
        self.assertEqual(decorator.for_, None)
        self.assertEqual(decorator.permission, None)
        
    def test_create_nondefaults(self):
        decorator = self._makeOne(name=None, request_type=None, for_=None,
                                  permission='foo')
        self.assertEqual(decorator.name, None)
        self.assertEqual(decorator.request_type, None)
        self.assertEqual(decorator.for_, None)
        self.assertEqual(decorator.permission, 'foo')
        
    def test_call_function(self):
        decorator = self._makeOne()
        def foo():
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__
        self.assertEqual(settings['permission'], None)
        self.assertEqual(settings['for_'], None)
        self.assertEqual(settings['request_type'], None)

    def test_call_oldstyle_class(self):
        decorator = self._makeOne()
        class foo:
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__
        self.assertEqual(settings['permission'], None)
        self.assertEqual(settings['for_'], None)
        self.assertEqual(settings['request_type'], None)

    def test_call_newstyle_class(self):
        decorator = self._makeOne()
        class foo(object):
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__
        self.assertEqual(settings['permission'], None)
        self.assertEqual(settings['for_'], None)
        self.assertEqual(settings['request_type'], None)

class TestDefaultForbiddenView(unittest.TestCase):
    def _callFUT(self, context, request):
        from repoze.bfg.view import default_forbidden_view
        return default_forbidden_view(context, request)

    def test_nomessage(self):
        request = DummyRequest({})
        context = DummyContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')
        self.failUnless('<code></code>' in response.body)

    def test_withmessage(self):
        request = DummyRequest({'repoze.bfg.message':'abc&123'})
        context = DummyContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')
        self.failUnless('<code>abc&amp;123</code>' in response.body)

class TestDefaultNotFoundView(unittest.TestCase):
    def _callFUT(self, context, request):
        from repoze.bfg.view import default_notfound_view
        return default_notfound_view(context, request)

    def test_nomessage(self):
        request = DummyRequest({})
        context = DummyContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')
        self.failUnless('<code></code>' in response.body)

    def test_withmessage(self):
        request = DummyRequest({'repoze.bfg.message':'abc&123'})
        context = DummyContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')
        self.failUnless('<code>abc&amp;123</code>' in response.body)

class AppendSlashNotFoundView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, context, request):
        from repoze.bfg.view import append_slash_notfound_view
        return append_slash_notfound_view(context, request)

    def _registerMapper(self, match=True):
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
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerUtility(mapper, IRoutesMapper)
        return mapper

    def test_no_mapper(self):
        request = DummyRequest({'PATH_INFO':'/abc'})
        context = DummyContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_no_path(self):
        self._registerMapper(True)
        request = DummyRequest({})
        context = DummyContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_mapper_path_already_slash_ending(self):
        self._registerMapper(True)
        request = DummyRequest({'PATH_INFO':'/abc/'})
        context = DummyContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_matches(self):
        self._registerMapper(True)
        request = DummyRequest({'PATH_INFO':'/abc'})
        context = DummyContext()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, '/abc/')

class TestMultiView(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.view import MultiView
        return MultiView

    def _makeOne(self, name='name'):
        return self._getTargetClass()(name)
    
    def test_class_implements_ISecuredView(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ISecuredView
        verifyClass(ISecuredView, self._getTargetClass())

    def test_instance_implements_ISecuredView(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ISecuredView
        verifyObject(ISecuredView, self._makeOne())

    def test_add(self):
        mv = self._makeOne()
        mv.add('view', 100)
        self.assertEqual(mv.views, [(100, 'view')])
        mv.add('view2', 99)
        self.assertEqual(mv.views, [(99, 'view2'), (100, 'view')])

    def test_match_not_found(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(NotFound, mv.match, context, request)

    def test_match_predicate_fails(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        def view(context, request):
            """ """
        view.__predicated__ = lambda *arg: False
        mv.views = [(100, view)]
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(NotFound, mv.match, context, request)

    def test_match_predicate_succeeds(self):
        mv = self._makeOne()
        def view(context, request):
            """ """
        view.__predicated__ = lambda *arg: True
        mv.views = [(100, view)]
        context = DummyContext()
        request = DummyRequest()
        result = mv.match(context, request)
        self.assertEqual(result, view)

    def test_permitted_no_views(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(NotFound, mv.__permitted__, context, request)

    def test_permitted_no_match_with__permitted__(self):
        mv = self._makeOne()
        def view(context, request):
            """ """
        mv.views = [(100, view)]
        context = DummyContext()
        request = DummyRequest()
        self.assertEqual(mv.__permitted__(None, None), True)
        
    def test_permitted(self):
        from zope.component import getSiteManager
        mv = self._makeOne()
        def view(context, request):
            """ """
        def permitted(context, request):
            return False
        view.__permitted__ = permitted
        mv.views = [(100, view)]
        context = DummyContext()
        request = DummyRequest()
        sm = getSiteManager()
        result = mv.__permitted__(context, request)
        self.assertEqual(result, False)

    def test__call__not_found(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(NotFound, mv, context, request)

    def test___call__intermediate_not_found(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        request.view_name = ''
        expected_response = DummyResponse()
        def view1(context, request):
            raise NotFound
        def view2(context, request):
            return expected_response
        mv.views = [(100, view1), (99, view2)]
        response = mv(context, request)
        self.assertEqual(response, expected_response)

    def test___call__(self):
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        request.view_name = ''
        expected_response = DummyResponse()
        def view(context, request):
            return expected_response
        mv.views = [(100, view)]
        response = mv(context, request)
        self.assertEqual(response, expected_response)

    def test__call_permissive__not_found(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(NotFound, mv, context, request)

    def test___call_permissive_has_call_permissive(self):
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        request.view_name = ''
        expected_response = DummyResponse()
        def view(context, request):
            """ """
        def permissive(context, request):
            return expected_response
        view.__call_permissive__ = permissive
        mv.views = [(100, view)]
        response = mv.__call_permissive__(context, request)
        self.assertEqual(response, expected_response)

    def test___call_permissive_has_no_call_permissive(self):
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        request.view_name = ''
        expected_response = DummyResponse()
        def view(context, request):
            return expected_response
        mv.views = [(100, view)]
        response = mv.__call_permissive__(context, request)
        self.assertEqual(response, expected_response)

class Test_map_view(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, view, *arg, **kw):
        from repoze.bfg.view import map_view
        return map_view(view, *arg, **kw)

    def _registerRenderer(self, name='.txt'):
        from repoze.bfg.interfaces import IRendererFactory
        from repoze.bfg.interfaces import ITemplateRenderer
        from zope.interface import implements
        from zope.component import getSiteManager
        class Renderer:
            implements(ITemplateRenderer)
            def __init__(self, path):
                pass
            def __call__(self, *arg):
                return 'Hello!'
        sm = getSiteManager()
        sm.registerUtility(Renderer, IRendererFactory, name=name)

    def test_view_as_function_context_and_request(self):
        def view(context, request):
            return 'OK'
        result = self._callFUT(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_function_with_attr(self):
        def view(context, request):
            """ """
        result = self._callFUT(view, attr='__name__')
        self.failIf(result is view)
        self.assertRaises(TypeError, result, None, None)

    def test_view_as_function_with_attr_and_renderer(self):
        self._registerRenderer()
        def view(context, request):
            """ """
        result = self._callFUT(view, attr='__name__',
                               renderer_name='fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertRaises(TypeError, result, None, None)
        
    def test_view_as_function_requestonly(self):
        def view(request):
            return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_function_requestonly_with_attr(self):
        def view(request):
            """ """
        result = self._callFUT(view, attr='__name__')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertRaises(TypeError, result, None, None)

    def test_view_as_newstyle_class_context_and_request(self):
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_newstyle_class_context_and_request_with_attr(self):
        class view(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return 'OK'
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_newstyle_class_context_and_request_with_attr_and_renderer(
        self):
        self._registerRenderer()
        class view(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self._callFUT(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')
        
    def test_view_as_newstyle_class_requestonly(self):
        class view(object):
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_newstyle_class_requestonly_with_attr(self):
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return 'OK'
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_newstyle_class_requestonly_with_attr_and_renderer(self):
        self._registerRenderer()
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self._callFUT(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_view_as_oldstyle_class_context_and_request(self):
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_oldstyle_class_context_and_request_with_attr(self):
        class view:
            def __init__(self, context, request):
                pass
            def index(self):
                return 'OK'
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_oldstyle_class_context_and_request_with_attr_and_renderer(
        self):
        self._registerRenderer()
        class view:
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self._callFUT(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_view_as_oldstyle_class_requestonly(self):
        class view:
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_oldstyle_class_requestonly_with_attr(self):
        class view:
            def __init__(self, request):
                pass
            def index(self):
                return 'OK'
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_oldstyle_class_requestonly_with_attr_and_renderer(self):
        self._registerRenderer()
        class view:
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self._callFUT(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_view_as_instance_context_and_request(self):
        class View:
            def __call__(self, context, request):
                return 'OK'
        view = View()
        result = self._callFUT(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')
        
    def test_view_as_instance_context_and_request_and_attr(self):
        class View:
            def index(self, context, request):
                return 'OK'
        view = View()
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_instance_context_and_request_attr_and_renderer(self):
        self._registerRenderer()
        class View:
            def index(self, context, request):
                return {'a':'1'}
        view = View()
        result = self._callFUT(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_view_as_instance_requestonly(self):
        class View:
            def __call__(self, request):
                return 'OK'
        view = View()
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_instance_requestonly_with_attr(self):
        class View:
            def index(self, request):
                return 'OK'
        view = View()
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_instance_requestonly_with_attr_and_renderer(self):
        self._registerRenderer()
        class View:
            def index(self, request):
                return {'a':'1'}
        view = View()
        result = self._callFUT(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_view_rendereronly(self):
        self._registerRenderer()
        def view(context, request):
            return {'a':'1'}
        result = self._callFUT(
            view,
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_view_defaultrendereronly(self):
        self._registerRenderer(name='')
        def view(context, request):
            return {'a':'1'}
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

class TestRequestOnly(unittest.TestCase):
    def _callFUT(self, arg):
        from repoze.bfg.view import requestonly
        return requestonly(arg)
    
    def test_newstyle_class_no_init(self):
        class foo(object):
            """ """
        self.assertFalse(self._callFUT(foo))

    def test_newstyle_class_init_toomanyargs(self):
        class foo(object):
            def __init__(self, context, request):
                """ """
        self.assertFalse(self._callFUT(foo))
        
    def test_newstyle_class_init_onearg_named_request(self):
        class foo(object):
            def __init__(self, request):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_onearg_named_somethingelse(self):
        class foo(object):
            def __init__(self, req):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_defaultargs_firstname_not_request(self):
        class foo(object):
            def __init__(self, context, request=None):
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_newstyle_class_init_defaultargs_firstname_request(self):
        class foo(object):
            def __init__(self, request, foo=1, bar=2):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_noargs(self):
        class foo(object):
            def __init__():
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_no_init(self):
        class foo:
            """ """
        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_init_toomanyargs(self):
        class foo:
            def __init__(self, context, request):
                """ """
        self.assertFalse(self._callFUT(foo))
        
    def test_oldstyle_class_init_onearg_named_request(self):
        class foo:
            def __init__(self, request):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_oldstyle_class_init_onearg_named_somethingelse(self):
        class foo:
            def __init__(self, req):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_oldstyle_class_init_defaultargs_firstname_not_request(self):
        class foo:
            def __init__(self, context, request=None):
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_init_defaultargs_firstname_request(self):
        class foo:
            def __init__(self, request, foo=1, bar=2):
                """ """
        self.assertTrue(self._callFUT(foo), True)

    def test_oldstyle_class_init_noargs(self):
        class foo:
            def __init__():
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_function_toomanyargs(self):
        def foo(context, request):
            """ """
        self.assertFalse(self._callFUT(foo))
        
    def test_function_onearg_named_request(self):
        def foo(request):
            """ """
        self.assertTrue(self._callFUT(foo))

    def test_function_onearg_named_somethingelse(self):
        def foo(req):
            """ """
        self.assertTrue(self._callFUT(foo))

    def test_function_defaultargs_firstname_not_request(self):
        def foo(context, request=None):
            """ """
        self.assertFalse(self._callFUT(foo))

    def test_function_defaultargs_firstname_request(self):
        def foo(request, foo=1, bar=2):
            """ """
        self.assertTrue(self._callFUT(foo), True)

    def test_instance_toomanyargs(self):
        class Foo:
            def __call__(self, context, request):
                """ """
        foo = Foo()
        self.assertFalse(self._callFUT(foo))
        
    def test_instance_defaultargs_onearg_named_request(self):
        class Foo:
            def __call__(self, request):
                """ """
        foo = Foo()
        self.assertTrue(self._callFUT(foo))

    def test_instance_defaultargs_onearg_named_somethingelse(self):
        class Foo:
            def __call__(self, req):
                """ """
        foo = Foo()
        self.assertTrue(self._callFUT(foo))

    def test_instance_defaultargs_firstname_not_request(self):
        class Foo:
            def __call__(self, context, request=None):
                """ """
        foo = Foo()
        self.assertFalse(self._callFUT(foo))

    def test_instance_defaultargs_firstname_request(self):
        class Foo:
            def __call__(self, request, foo=1, bar=2):
                """ """
        foo = Foo()
        self.assertTrue(self._callFUT(foo), True)

    def test_instance_nocall(self):
        class Foo: pass
        foo = Foo()
        self.assertFalse(self._callFUT(foo))

class TestDecorateView(unittest.TestCase):
    def _callFUT(self, wrapped, original):
        from repoze.bfg.view import decorate_view
        return decorate_view(wrapped, original)
    
    def test_it_same(self):
        def view(context, request):
            """ """
        result = self._callFUT(view, view)
        self.assertEqual(result, False)

    def test_it_different(self):
        class DummyView1:
            """ 1 """
            __name__ = '1'
            __module__ = '1'
            def __call__(self, context, request):
                """ """
            def __call_permissive__(self, context, reuqest):
                """ """
            def __predicated__(self, context, reuqest):
                """ """
            def __permitted__(self, context, request):
                """ """
        class DummyView2:
            """ 2 """
            __name__ = '2'
            __module__ = '2'
            def __call__(self, context, request):
                """ """
            def __call_permissive__(self, context, reuqest):
                """ """
            def __predicated__(self, context, reuqest):
                """ """
            def __permitted__(self, context, request):
                """ """
        view1 = DummyView1()
        view2 = DummyView2()
        result = self._callFUT(view1, view2)
        self.assertEqual(result, True)
        self.failUnless(view1.__doc__ is view2.__doc__)
        self.failUnless(view1.__module__ is view2.__module__)
        self.failUnless(view1.__name__ is view2.__name__)
        self.failUnless(view1.__call_permissive__.im_func is
                        view2.__call_permissive__.im_func)
        self.failUnless(view1.__permitted__.im_func is
                        view2.__permitted__.im_func)
        self.failUnless(view1.__predicated__.im_func is
                        view2.__predicated__.im_func)

class Test_rendered_response(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, renderer, response, view=None,
                 context=None, request=None, renderer_name=None):
        from repoze.bfg.view import rendered_response
        if request is None:
            request = DummyRequest()
        return rendered_response(renderer, response, view,
                                 context, request, renderer_name)

    def _makeRenderer(self):
        def renderer(*arg):
            return 'Hello!'
        return renderer

    def test_is_response(self):
        renderer = self._makeRenderer()
        response = DummyResponse()
        result = self._callFUT(renderer, response)
        self.assertEqual(result, response)

    def test_calls_renderer(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        result = self._callFUT(renderer, response)
        self.assertEqual(result.body, 'Hello!')

    def test_with_content_type(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = DummyRequest()
        attrs = {'response_content_type':'text/nonsense'}
        request.environ['webob.adhoc_attrs'] = attrs
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.content_type, 'text/nonsense')

    def test_with_headerlist(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = DummyRequest()
        attrs = {'response_headerlist':[('a', '1'), ('b', '2')]}
        request.environ['webob.adhoc_attrs'] = attrs
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.headerlist,
                         [('Content-Type', 'text/html; charset=UTF-8'),
                          ('Content-Length', '6'),
                          ('a', '1'),
                          ('b', '2')])

    def test_with_status(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = DummyRequest()
        attrs = {'response_status':'406 You Lose'}
        request.environ['webob.adhoc_attrs'] = attrs
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.status, '406 You Lose')

    def test_with_charset(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = DummyRequest()
        attrs = {'response_charset':'UTF-16'}
        request.environ['webob.adhoc_attrs'] = attrs
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.charset, 'UTF-16')

    def test_with_cache_for(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = DummyRequest()
        attrs = {'response_cache_for':100}
        request.environ['webob.adhoc_attrs'] = attrs
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.cache_control.max_age, 100)

class TestDeriveView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, view, *arg, **kw):
        from repoze.bfg.view import derive_view
        return derive_view(view, *arg, **kw)

    def _registerLogger(self):
        from repoze.bfg.interfaces import ILogger
        from zope.component import getSiteManager
        logger = DummyLogger()
        sm = getSiteManager()
        sm.registerUtility(logger, ILogger, 'repoze.bfg.debug')
        return logger

    def _registerSettings(self, **settings):
        from repoze.bfg.interfaces import ISettings
        from zope.component import getSiteManager
        sm = getSiteManager()
        sm.registerUtility(settings, ISettings)

    def _registerSecurityPolicy(self, permissive):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from zope.component import getSiteManager
        policy = DummySecurityPolicy(permissive)
        sm = getSiteManager()
        sm.registerUtility(policy, IAuthenticationPolicy)
        sm.registerUtility(policy, IAuthorizationPolicy)
    
    def test_view_as_function_context_and_request(self):
        def view(context, request):
            return 'OK'
        result = self._callFUT(view)
        self.failUnless(result is view)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(view(None, None), 'OK')
        
    def test_view_as_function_requestonly(self):
        def view(request):
            return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_newstyle_class_context_and_request(self):
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')
        
    def test_view_as_newstyle_class_requestonly(self):
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_oldstyle_class_context_and_request(self):
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')
        
    def test_view_as_oldstyle_class_requestonly(self):
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_instance_context_and_request(self):
        class View:
            def __call__(self, context, request):
                return 'OK'
        view = View()
        result = self._callFUT(view)
        self.failUnless(result is view)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')
        
    def test_view_as_instance_requestonly(self):
        class View:
            def __call__(self, request):
                return 'OK'
        view = View()
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')

    def test_view_with_debug_authorization_no_authpol(self):
        def view(context, request):
            return 'OK'
        self._registerSettings(debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        result = self._callFUT(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        request = DummyRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), 'OK')
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): Allowed "
                         "(no authorization policy in use)")

    def test_view_with_debug_authorization_no_permission(self):
        def view(context, request):
            return 'OK'
        self._registerSettings(debug_authorization=True, reload_templates=True)
        self._registerSecurityPolicy(True)
        logger = self._registerLogger()
        result = self._callFUT(view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        request = DummyRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), 'OK')
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): Allowed ("
                         "no permission registered)")

    def test_view_with_debug_authorization_permission_authpol_permitted(self):
        def view(context, request):
            return 'OK'
        self._registerSettings(debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        self._registerSecurityPolicy(True)
        result = self._callFUT(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result.__call_permissive__, view)
        request = DummyRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), 'OK')
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): True")
        
    def test_view_with_debug_authorization_permission_authpol_denied(self):
        from repoze.bfg.exceptions import Forbidden
        def view(context, request):
            """ """
        self._registerSettings(debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        self._registerSecurityPolicy(False)
        result = self._callFUT(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result.__call_permissive__, view)
        request = DummyRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertRaises(Forbidden, result, None, request)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): False")

    def test_view_with_debug_authorization_permission_authpol_denied2(self):
        def view(context, request):
            """ """
        self._registerSettings(debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        self._registerSecurityPolicy(False)
        result = self._callFUT(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        permitted = result.__permitted__(None, None)
        self.assertEqual(permitted, False)

    def test_view_with_predicates_all(self):
        def view(context, request):
            return '123'
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return True
        result = self._callFUT(view, predicates=[predicate1, predicate2])
        request = DummyRequest()
        request.method = 'POST'
        next = result(None, None)
        self.assertEqual(next, '123')
        self.assertEqual(predicates, [True, True])

    def test_view_with_predicates_notall(self):
        from repoze.bfg.exceptions import NotFound
        def view(context, request):
            """ """
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return False
        result = self._callFUT(view, predicates=[predicate1, predicate2])
        request = DummyRequest()
        request.method = 'POST'
        self.assertRaises(NotFound, result, None, None)
        self.assertEqual(predicates, [True, True])

    def test_view_with_predicates_checker(self):
        def view(context, request):
            """ """
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return True
        result = self._callFUT(view, predicates=[predicate1, predicate2])
        request = DummyRequest()
        request.method = 'POST'
        next = result.__predicated__(None, None)
        self.assertEqual(next, True)
        self.assertEqual(predicates, [True, True])

    def test_view_with_wrapper_viewname(self):
        from webob import Response
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IView
        inner_response = Response('OK')
        def inner_view(context, request):
            return inner_response
        def outer_view(context, request):
            self.assertEqual(request.wrapped_response, inner_response)
            self.assertEqual(request.wrapped_body, inner_response.body)
            self.assertEqual(request.wrapped_view, inner_view)
            return Response('outer ' + request.wrapped_body)
        sm = getSiteManager()
        sm.registerAdapter(outer_view, (None, None), IView, 'owrap')
        result = self._callFUT(inner_view, viewname='inner',
                               wrapper_viewname='owrap')
        self.failIf(result is inner_view)
        self.assertEqual(inner_view.__module__, result.__module__)
        self.assertEqual(inner_view.__doc__, result.__doc__)
        request = DummyRequest()
        response = result(None, request)
        self.assertEqual(response.body, 'outer OK')

    def test_view_with_wrapper_viewname_notfound(self):
        from webob import Response
        inner_response = Response('OK')
        def inner_view(context, request):
            return inner_response
        request = DummyRequest()
        wrapped = self._callFUT(
            inner_view, viewname='inner', wrapper_viewname='owrap')
        result = self.assertRaises(ValueError, wrapped, None, request)

class TestAll(unittest.TestCase):
    def test_it(self):
        from repoze.bfg.view import all
        self.assertEqual(all([True, True]), True)
        self.assertEqual(all([False, False]), False)
        self.assertEqual(all([False, True]), False)


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
            
class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    warn = info
    debug = info

class DummySecurityPolicy:
    def __init__(self, permitted=True):
        self.permitted = permitted

    def effective_principals(self, request):
        return []

    def permits(self, context, principals, permission):
        return self.permitted
