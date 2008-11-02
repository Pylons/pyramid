import unittest

from zope.component.testing import PlacelessSetup

class BaseTest(PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

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

    def _makeEnviron(self, **extras):
        environ = {
            'wsgi.url_scheme':'http',
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'8080',
            'REQUEST_METHOD':'GET',
            }
        environ.update(extras)
        return environ

class RenderViewToResponseTests(unittest.TestCase, BaseTest):
    def _getFUT(self):
        from repoze.bfg.view import render_view_to_response
        return render_view_to_response
    
    def test_call_no_view_registered(self):
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        context = DummyContext()
        renderer = self._getFUT()
        result = renderer(context, request, name='notregistered')
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
        permissionfactory = make_permission_factory(False)
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, 'registered', IContext,
                                 IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        from repoze.bfg.security import Unauthorized
        self.assertRaises(Unauthorized, renderer, context, request,
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
        permissionfactory = make_permission_factory(True)
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, 'registered', IContext,
                                 IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        response = renderer(context, request, name='registered', secure=True)
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
        permissionfactory = make_permission_factory(False)
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, 'registered', IContext,
                                 IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        response = renderer(context, request, name='registered', secure=False)
        self.assertEqual(response.status, '200 OK')


    def test_call_view_response_doesnt_implement_IResponse(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = 'abc'
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        self.assertRaises(ValueError, renderer, context, request,
                          name='registered', secure=False)


class RenderViewToIterableTests(unittest.TestCase, BaseTest):
    def _getFUT(self):
        from repoze.bfg.view import render_view_to_iterable
        return render_view_to_iterable
    
    def test_call_no_view_registered(self):
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        context = DummyContext()
        renderer = self._getFUT()
        result = renderer(context, request, name='notregistered')
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
        permissionfactory = make_permission_factory(False)
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, 'registered', IContext,
                                 IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        from repoze.bfg.security import Unauthorized
        self.assertRaises(Unauthorized, renderer, context, request,
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
        permissionfactory = make_permission_factory(True)
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, 'registered', IContext,
                                 IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        iterable = renderer(context, request, name='registered', secure=True)
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
        permissionfactory = make_permission_factory(False)
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, 'registered', IContext,
                                 IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        iterable = renderer(context, request, name='registered', secure=False)
        self.assertEqual(iterable, ())

    def test_call_view_response_doesnt_implement_IResponse(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = 'abc'
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        self.assertRaises(ValueError, renderer, context, request,
                          name='registered', secure=False)

class RenderViewTests(unittest.TestCase, BaseTest):
    def _getFUT(self):
        from repoze.bfg.view import render_view
        return render_view
    
    def test_call_no_view_registered(self):
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        context = DummyContext()
        renderer = self._getFUT()
        result = renderer(context, request, name='notregistered')
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
        permissionfactory = make_permission_factory(False)
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, 'registered', IContext,
                                 IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        from repoze.bfg.security import Unauthorized
        self.assertRaises(Unauthorized, renderer, context, request,
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
        permissionfactory = make_permission_factory(True)
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, 'registered', IContext,
                                 IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        s = renderer(context, request, name='registered', secure=True)
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
        permissionfactory = make_permission_factory(False)
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        self._registerSecurityPolicy(secpol)
        self._registerPermission(permissionfactory, 'registered', IContext,
                                 IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        s = renderer(context, request, name='registered', secure=False)
        self.assertEqual(s, '')

    def test_call_view_response_doesnt_implement_IResponse(self):
        context = DummyContext()
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        directlyProvides(context, IContext)
        response = 'abc'
        view = make_view(response)
        self._registerView(view, 'registered', IContext, IRequest)
        environ = self._makeEnviron()
        from webob import Request
        request = Request(environ)
        directlyProvides(request, IRequest)
        renderer = self._getFUT()
        self.assertRaises(ValueError, renderer, context, request,
                          name='registered', secure=False)

class TestIsResponse(unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.view import is_response
        return is_response

    def test_is(self):
        response = DummyResponse()
        f = self._getFUT()
        self.assertEqual(f(response), True)

    def test_isnt(self):
        response = None
        f = self._getFUT()
        self.assertEqual(f(response), False)

class TestViewExecutionPermitted(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.view import view_execution_permitted
        return view_execution_permitted(*arg, **kw)

    def _registerSecurityPolicy(self, secpol):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import ISecurityPolicy
        gsm.registerUtility(secpol, ISecurityPolicy)

    def _registerPermission(self, permission, name, *for_):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import IViewPermission
        gsm.registerAdapter(permission, for_, IViewPermission, name)

    def test_no_secpol(self):
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, '')
        msg = result.msg
        self.failUnless("Allowed: view name '' in context" in msg)
        self.failUnless('(no security policy in use)' in msg)
        self.assertEqual(result, True)

    def test_secpol_no_permission(self):
        secpol = DummySecurityPolicy()
        self._registerSecurityPolicy(secpol)
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, '')
        msg = result.msg
        self.failUnless("Allowed: view name '' in context" in msg)
        self.failUnless("(no permission registered for name '')" in msg)
        self.assertEqual(result, True)

    def test_secpol_and_permission(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        class IContext(Interface):
            pass
        context = DummyContext()
        directlyProvides(context, IContext)
        permissionfactory = make_permission_factory(True)
        self._registerPermission(permissionfactory, '', IContext,
                                 IRequest)
        secpol = DummySecurityPolicy()
        self._registerSecurityPolicy(secpol)
        request = DummyRequest()
        directlyProvides(request, IRequest)
        result = self._callFUT(context, request, '')
        self.failUnless(result is True)

class DummyContext:
    pass

class DummyRequest:
    pass

def make_view(response):
    def view(context, request):
        return response
    return view

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

def make_appcontext():
    from zope.configuration.interfaces import IConfigurationContext
    from zope.interface import directlyProvides
    app_context = DummyContext()
    directlyProvides(app_context, IConfigurationContext)
    return app_context

class DummyResponse:
    status = '200 OK'
    headerlist = ()
    app_iter = ()
    
class DummySecurityPolicy:
    pass

