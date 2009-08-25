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

    def _registerViewPermission(self, view_name, allow=True):
        import zope.component
        from zope.interface import Interface
        from repoze.bfg.interfaces import IViewPermission
        class Checker(object):
            def __call__(self, context, request):
                self.context = context
                self.request = request
                return allow
        checker = Checker()
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerAdapter(checker, (Interface, Interface),
                            IViewPermission,
                            view_name)
        return checker

    def _registerSecurityPolicy(self, secpol):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import ISecurityPolicy
        gsm.registerUtility(secpol, ISecurityPolicy)

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

    def test_call_view_registered_secure_permission_disallows(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        secpol = DummySecurityPolicy()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerViewPermission('registered', False)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        from repoze.bfg.security import Unauthorized
        self.assertRaises(Unauthorized, self._callFUT, context, request,
                          name='registered', secure=True)

    def test_call_view_registered_secure_permission_allows(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        secpol = DummySecurityPolicy()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerViewPermission('registered', True)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        response = self._callFUT(context, request, name='registered',
                                 secure=True)
        self.assertEqual(response.status, '200 OK')

    def test_call_view_registered_insecure_permission_disallows(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        secpol = DummySecurityPolicy()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerViewPermission('registered', False)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        response = self._callFUT(context, request, name='registered',
                                 secure=False)
        self.assertEqual(response.status, '200 OK')

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

    def test_call_view_registered_secure_permission_disallows(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        secpol = DummySecurityPolicy()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerViewPermission('registered', False)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        from repoze.bfg.security import Unauthorized
        self.assertRaises(Unauthorized, self._callFUT, context, request,
                          name='registered', secure=True)

    def test_call_view_registered_secure_permission_allows(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        secpol = DummySecurityPolicy()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerViewPermission('registered', True)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        iterable = self._callFUT(context, request, name='registered',
                                 secure=True)
        self.assertEqual(iterable, ())

    def test_call_view_registered_insecure_permission_disallows(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        secpol = DummySecurityPolicy()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerViewPermission('registered', False)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        iterable = self._callFUT(context, request, name='registered',
                                 secure=False)
        self.assertEqual(iterable, ())

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

    def test_call_view_registered_secure_permission_disallows(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        secpol = DummySecurityPolicy()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerViewPermission('registered', False)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        from repoze.bfg.security import Unauthorized
        self.assertRaises(Unauthorized, self._callFUT, context, request,
                          name='registered', secure=True)

    def test_call_view_registered_secure_permission_allows(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        secpol = DummySecurityPolicy()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerViewPermission('registered', True)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        s = self._callFUT(context, request, name='registered', secure=True)
        self.assertEqual(s, '')

    def test_call_view_registered_insecure_permission_disallows(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = DummyResponse()
        secpol = DummySecurityPolicy()
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerViewPermission('registered', False)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        s = self._callFUT(context, request, name='registered', secure=False)
        self.assertEqual(s, '')

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
        self.assertEqual(wrapped.__is_bfg_view__, True)
        self.assertEqual(wrapped.__permission__, None)
        self.assertEqual(wrapped.__for__, None)
        self.assertEqual(wrapped.__request_type__, None)

    def test_call_oldstyle_class(self):
        import inspect
        decorator = self._makeOne()
        class foo:
            """ docstring """
            def __init__(self, context, request):
                self.context = context
                self.request = request
            def __call__(self):
                return self
        wrapped = decorator(foo)
        self.failIf(wrapped is foo)
        self.failUnless(inspect.isfunction(wrapped))
        self.assertEqual(wrapped.__is_bfg_view__, True)
        self.assertEqual(wrapped.__permission__, None)
        self.assertEqual(wrapped.__for__, None)
        self.assertEqual(wrapped.__request_type__, None)
        self.assertEqual(wrapped.__module__, foo.__module__)
        self.assertEqual(wrapped.__name__, foo.__name__)
        self.assertEqual(wrapped.__doc__, foo.__doc__)
        result = wrapped(None, None)
        self.assertEqual(result.context, None)
        self.assertEqual(result.request, None)

    def test_call_newstyle_class(self):
        import inspect
        decorator = self._makeOne()
        class foo(object):
            """ docstring """
            def __init__(self, context, request):
                self.context = context
                self.request = request
            def __call__(self):
                return self
        wrapped = decorator(foo)
        self.failIf(wrapped is foo)
        self.failUnless(inspect.isfunction(wrapped))
        self.assertEqual(wrapped.__is_bfg_view__, True)
        self.assertEqual(wrapped.__permission__, None)
        self.assertEqual(wrapped.__for__, None)
        self.assertEqual(wrapped.__request_type__, None)
        self.assertEqual(wrapped.__module__, foo.__module__)
        self.assertEqual(wrapped.__name__, foo.__name__)
        self.assertEqual(wrapped.__doc__, foo.__doc__)
        result = wrapped(None, None)
        self.assertEqual(result.context, None)
        self.assertEqual(result.request, None)

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
    app_iter = ()
    
class DummySecurityPolicy:
    pass

