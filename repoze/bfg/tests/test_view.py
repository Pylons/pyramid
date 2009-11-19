import unittest

from repoze.bfg.testing import cleanUp

class BaseTest(object):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _registerView(self, app, name, *for_):
        import zope.component
        sm = zope.component.getSiteManager()
        from repoze.bfg.interfaces import IView
        sm.registerAdapter(app, for_, IView, name)

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
        settings = wrapped.__bfg_view_settings__[0]
        self.assertEqual(settings['permission'], None)
        self.assertEqual(settings['for_'], None)
        self.assertEqual(settings['request_type'], None)

    def test_call_oldstyle_class(self):
        decorator = self._makeOne()
        class foo:
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__[0]
        self.assertEqual(settings['permission'], None)
        self.assertEqual(settings['for_'], None)
        self.assertEqual(settings['request_type'], None)

    def test_call_newstyle_class(self):
        decorator = self._makeOne()
        class foo(object):
            """ docstring """
        wrapped = decorator(foo)
        self.failUnless(wrapped is foo)
        settings = wrapped.__bfg_view_settings__[0]
        self.assertEqual(settings['permission'], None)
        self.assertEqual(settings['for_'], None)
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
        sm = zope.component.getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
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
